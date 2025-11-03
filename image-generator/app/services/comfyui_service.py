import json
import httpx
import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from ..repositories.configuration_repository import ConfigurationRepository


class ComfyUIService:
    def __init__(self, db: Session, comfyui_url: str = "http://localhost:8188"):
        self.db = db
        self.comfyui_url = comfyui_url.rstrip('/')
        self.config_repo = ConfigurationRepository(db)
        self.logger = logging.getLogger(__name__)
    
    def replace_placeholders(self, workflow: Dict[str, Any], values: Dict[str, Any]) -> Dict[str, Any]:
        if isinstance(workflow, dict):
            result = {}
            for key, value in workflow.items():
                result[key] = self.replace_placeholders(value, values)
            return result
        elif isinstance(workflow, list):
            return [self.replace_placeholders(item, values) for item in workflow]
        elif isinstance(workflow, str):
            result = workflow
            for placeholder_name, placeholder_value in values.items():
                placeholder_pattern = f"{{{{{placeholder_name}}}}}"
                if placeholder_pattern in result:
                    if result == placeholder_pattern:
                        return placeholder_value
                    result = result.replace(placeholder_pattern, str(placeholder_value))
            return result
        else:
            return workflow
    
    async def generate_image(
        self,
        config_key: Optional[str] = None,
        config_uuid: Optional[str] = None,
        placeholders: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        if placeholders is None:
            placeholders = {}
        
        if config_key:
            config = self.config_repo.get_configuration_by_key(config_key)
        elif config_uuid:
            config = self.config_repo.get_configuration_by_uuid(config_uuid)
        else:
            config = self.config_repo.get_default_configuration()
        
        if not config:
            raise ValueError("Configuration not found")

        try:
            workflow = json.loads(config.configuration)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration: {e}")
        
        workflow = self.replace_placeholders(workflow, placeholders)
        
        self.logger.info(f"Prepared workflow for ComfyUI with placeholders: {list(placeholders.keys())}")
        
        try:
            async with httpx.AsyncClient(timeout=300.0) as client:
                payload = {"prompt": workflow}
                
                sample_keys = list(workflow.keys())[:3] if workflow else []
                self.logger.info(f"Sending workflow with nodes: {sample_keys}...")
                
                response = await client.post(
                    f"{self.comfyui_url}/prompt",
                    json=payload
                )

                if response.status_code != 200:
                    error_text = response.text
                    self.logger.error(f"ComfyUI returned status {response.status_code}")
                    self.logger.error(f"ComfyUI error response: {error_text}")
                    
                    # Пытаемся распарсить JSON ошибку
                    try:
                        error_json = response.json()
                        if 'error' in error_json:
                            self.logger.error(f"ComfyUI error details: {error_json['error']}")
                        if 'node_errors' in error_json:
                            self.logger.error(f"ComfyUI node errors: {error_json['node_errors']}")
                    except:
                        pass
                
                response.raise_for_status()
                result = response.json()
                
                prompt_id = result.get("prompt_id")
                self.logger.info(f"ComfyUI generation queued with prompt_id: {prompt_id}")
                
                return {
                    "prompt_id": prompt_id,
                    "status": "queued",
                    "number": result.get("number"),
                    "workflow": workflow
                }
        except httpx.HTTPStatusError as e:
            self.logger.error(f"ComfyUI API HTTP error: {e}")
            self.logger.error(f"Response body: {e.response.text if hasattr(e, 'response') else 'N/A'}")
            raise Exception(f"Failed to communicate with ComfyUI (HTTP {e.response.status_code if hasattr(e, 'response') else 'N/A'}): {e}")
        except httpx.HTTPError as e:
            self.logger.error(f"ComfyUI API error: {e}")
            raise Exception(f"Failed to communicate with ComfyUI: {e}")
    
    async def get_generation_status(self, prompt_id: str) -> Dict[str, Any]:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.comfyui_url}/history/{prompt_id}"
                )
                response.raise_for_status()
                history = response.json()
                
                if prompt_id in history:
                    prompt_data = history[prompt_id]
                    status = prompt_data.get("status", {})
                    
                    if status.get("completed", False):
                        return {
                            "status": "completed",
                            "data": prompt_data
                        }
                    elif "error" in status:
                        return {
                            "status": "failed",
                            "error": status.get("error"),
                            "data": prompt_data
                        }
                    else:
                        return {
                            "status": "processing",
                            "data": prompt_data
                        }
                else:
                    return {
                        "status": "not_found",
                        "data": None
                    }
        except httpx.HTTPError as e:
            self.logger.error(f"ComfyUI API error while getting status: {e}")
            raise Exception(f"Failed to get status from ComfyUI: {e}")
    
    async def get_generated_images(self, prompt_id: str) -> list[bytes]:
        status_result = await self.get_generation_status(prompt_id)
        
        if status_result["status"] != "completed":
            self.logger.warning(f"Generation not completed, status: {status_result['status']}")
            return []
        
        outputs = status_result["data"].get("outputs", {})
        images = []
        
        try:
            import base64
            async with httpx.AsyncClient(timeout=60.0) as client:
                for node_id, node_output in outputs.items():
                    if "images" in node_output:
                        for image_data in node_output["images"]:
                            if isinstance(image_data, str):
                                self.logger.info(f"Decoding base64 image from node {node_id}")
                                image_bytes = base64.b64decode(image_data)
                                images.append(image_bytes)
                            elif isinstance(image_data, dict):
                                filename = image_data.get("filename")
                                subfolder = image_data.get("subfolder", "")
                                folder_type = image_data.get("type", "output")
                                
                                params = {
                                    "filename": filename,
                                    "subfolder": subfolder,
                                    "type": folder_type
                                }
                                response = await client.get(
                                    f"{self.comfyui_url}/view",
                                    params=params
                                )
                                response.raise_for_status()
                                images.append(response.content)
                                
                                self.logger.info(f"Downloaded image: {filename}")
                            else:
                                self.logger.warning(f"Unknown image data type in node {node_id}: {type(image_data)}")
        except httpx.HTTPError as e:
            self.logger.error(f"Failed to download images: {e}")
            raise Exception(f"Failed to download images from ComfyUI: {e}")
        except Exception as e:
            self.logger.error(f"Failed to process images: {e}")
            raise Exception(f"Failed to process images from ComfyUI: {e}")
        
        return images
    
    async def wait_for_completion(
        self, 
        prompt_id: str, 
        poll_interval: float = 2.0,
        max_wait_time: float = 600.0
    ) -> Dict[str, Any]:
        import asyncio
        elapsed_time = 0.0
        
        while elapsed_time < max_wait_time:
            status = await self.get_generation_status(prompt_id)
            
            if status["status"] == "completed":
                return status
            elif status["status"] == "failed":
                raise Exception(f"Generation failed: {status.get('error')}")
            
            await asyncio.sleep(poll_interval)
            elapsed_time += poll_interval
        
        raise TimeoutError(f"Generation timeout after {max_wait_time} seconds")

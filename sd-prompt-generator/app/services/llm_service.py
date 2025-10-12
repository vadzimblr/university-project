import logging
import sys

import httpx
import json
import re
import os
from typing import Dict, Any

from app.models.schemas.internal import PreviousContext
from app.models.schemas.response import Character, Location, LLMSceneResponse, SceneResponse


class LLMService:
    def __init__(self):
        self.api_url = os.getenv("QWEN_API_URL")
        self.model = os.getenv("QWEN_MODEL")
        self.basic_auth_login = os.getenv("QWEN_AUTH_LOGIN")
        self.basic_auth_password = os.getenv("QWEN_AUTH_PASSWORD")
        self.timeout = 200
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(logging.StreamHandler(sys.stdout))

    def process_scene(self, scene_text: str, context: PreviousContext | None) -> LLMSceneResponse:
        prompt = self._build_prompt(scene_text, context)
        response_data = self._call_qwen(prompt)

        return self._parse_response(response_data)

    def _call_qwen(self, prompt: str) -> Dict[str, Any]:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }

        with httpx.Client(timeout=self.timeout) as client:
            self.logger.info(prompt)
            response = client.post(
                self.api_url,
                json=payload,
                headers={"Content-Type": "application/json"},
                auth = (self.basic_auth_login, self.basic_auth_password)
            )
            response.raise_for_status()

            result = response.json()
            clean = re.sub(r"^```json\s*|\s*```$", "", result['response'].strip())
            data = json.loads(clean)
            return data

    def _get_system_prompt(self) -> str:
        return """
            Ты – эксперт по анализу литературных сцен для создания изображений в Stable Diffusion.
            ТВОЯ ЗАДАЧА:
            1. Найди всех персонажей (свяжи с предыдущими, если это возможно).
            2. Извлеки только визуальную информацию, которую можно изобразить на одном статичном кадре.
            3. Сформируй визуальный промпт для Stable Diffusion.
            О SD_PROMPT:
            - Это краткое текстовое описание сцены, которое будет подано в нейросеть Stable Diffusion
              для генерации одной картинки.
            - Оно должно включать: место, освещение, настроение, внешний вид и позы персонажей,
              характерные предметы или детали окружения.
            - Стиль описания — как фотография: только наблюдаемые характеристики.
            - Никаких действий во времени, диалогов, мыслей, эмоций, метафор, повествовательных глаголов.
            ВAЖНО:
            - ОТВЕТ НА АНГЛИЙСКОМ.
            - Используй конкретные визуальные детали: цвет, фактуру, архитектуру, освещение.
            - В поле "actions" пиши только статичные позы или расположение персонажей,
              без динамики или речи. Выделяй самые важные и не противоречивые друг другу.
            ФОРМАТ ОТВЕТА (верни только JSON):
            {
              "characters": [
                {
                  "name": "string",         // имя или установившееся обозначение персонажа
                  "description": "string"   // краткое визуальное описание: одежда, возраст, отличительные черты
                }
              ],
              "location": "string",         // статичное описание места и освещения
              "actions": [ "string" ],      // статичные позы или расположение персонажей
              "sd_prompt": "string"         // готовый текст для Stable Diffusion в стиле фотографического описания
            }
        """

    def _build_prompt(self, scene_text: str, context: PreviousContext | None) -> str:
        system = self._get_system_prompt().strip()
        self.logger.info(context)
        previous_context = None

        if context is not None:
            previous_context = self.__build_previous_context_prompt_part(context)

        return f"""
            {system}
            ПРЕДЫДУЩИЙ КОНТЕКСТ:
            {previous_context if previous_context else "Нет предыдущего контекста"}
            ТЕКУЩАЯ СЦЕНА:
            {scene_text}
        """


    def __build_previous_context_prompt_part(self, context: PreviousContext) -> str:
        context_parts = []

        if context.characters:
            characters_text = "ИЗВЕСТНЫЕ ПЕРСОНАЖИ:\n" + "\n".join(
                f"- {char.name}: {char.description}" for char in context.characters
            )
            context_parts.append(characters_text)

        if context.location:
            location_text = f"ИЗВЕСТНАЯ ЛОКАЦИЯ:\n- {context.location.description}"
            context_parts.append(location_text)

        if context.actions:
            actions_text = "ПРЕДЫДУЩИЕ ДЕЙСТВИЯ:\n" + "\n".join(f"- {action}" for action in context.actions)
            context_parts.append(actions_text)

        context_str = "\n\n".join(context_parts)

        return context_str

    def _parse_response(self, response_data: Dict[str, Any]) -> LLMSceneResponse:
        characters = [
            Character(
                name=char_data["name"],
                description=char_data["description"]
            )
            for char_data in response_data["characters"]
        ]

        return LLMSceneResponse(
            characters=characters,
            location=response_data["location"],
            actions=response_data["actions"],
            sd_prompt=response_data["sd_prompt"]
        )

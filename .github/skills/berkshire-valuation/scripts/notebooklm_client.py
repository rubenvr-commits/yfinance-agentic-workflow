#!/usr/bin/env python3
"""Conexión a NotebookLM usando notebooklm-py.

Este script utiliza la autenticación guardada de NotebookLM y expone comandos
útiles para listar notebooks, crear notebooks y preguntar a un notebook.

Requisitos:
- `notebooklm-py` instalado en el entorno Python activo.
- Autenticación guardada con `NotebookLMClient.from_storage()` o configurada
  mediante `NOTEBOOKLM_AUTH_JSON` / el cliente oficial de NotebookLM.
"""

import argparse
import asyncio
import json
from pathlib import Path
from typing import Any

from notebooklm import NotebookLMClient, NotebookLMError


async def create_client(storage_path: str | None = None, profile: str | None = None):
    return await NotebookLMClient.from_storage(path=storage_path, profile=profile)


def pretty_print(data: Any) -> None:
    print(json.dumps(data, indent=2, default=str, ensure_ascii=False))


async def cmd_list(args: argparse.Namespace) -> int:
    async with await create_client(args.storage_path, args.profile) as client:
        notebooks = await client.notebooks.list()
        result = [
            {
                "id": nb.id,
                "title": nb.title,
                "sources_count": nb.sources_count,
                "created_at": nb.created_at,
            }
            for nb in notebooks
        ]
        pretty_print(result)
    return 0


async def cmd_create(args: argparse.Namespace) -> int:
    async with await create_client(args.storage_path, args.profile) as client:
        notebook = await client.notebooks.create(args.title)
        pretty_print({"id": notebook.id, "title": notebook.title})
    return 0


async def cmd_ask(args: argparse.Namespace) -> int:
    async with await create_client(args.storage_path, args.profile) as client:
        result = await client.chat.ask(
            args.notebook_id,
            args.question,
            conversation_id=args.conversation_id,
        )
        output = {
            "answer": result.answer,
            "conversation_id": result.conversation_id,
            "turn_number": result.turn_number,
            "is_follow_up": result.is_follow_up,
            "references": [
                {
                    "source_id": ref.source_id,
                    "cursor": getattr(ref, "cursor", None),
                    "citation_number": getattr(ref, "citation_number", None),
                    "start_char": getattr(ref, "start_char", None),
                    "end_char": getattr(ref, "end_char", None),
                    "cited_text": getattr(ref, "cited_text", None),
                }
                for ref in result.references
            ],
            "raw_response": result.raw_response,
        }
        pretty_print(output)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Herramienta de conexión a NotebookLM usando notebooklm-py."
    )
    parser.add_argument(
        "--storage-path",
        help="Ruta a storage_state.json de NotebookLM (toma prioridad sobre profile).",
    )
    parser.add_argument(
        "--profile",
        help="Nombre de perfil de NotebookLM para cargar autenticación.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list", help="Listar notebooks disponibles.")
    list_parser.set_defaults(func=cmd_list)

    create_parser = subparsers.add_parser("create", help="Crear un nuevo notebook.")
    create_parser.add_argument("title", help="Título del notebook a crear.")
    create_parser.set_defaults(func=cmd_create)

    ask_parser = subparsers.add_parser("ask", help="Preguntar a un notebook existente.")
    ask_parser.add_argument("--notebook-id", required=True, help="ID del notebook.")
    ask_parser.add_argument("--question", required=True, help="Pregunta para el notebook.")
    ask_parser.add_argument(
        "--conversation-id",
        help="ID de conversación previa para continuidad (opcional).",
    )
    ask_parser.set_defaults(func=cmd_ask)

    return parser


async def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return await args.func(args)
    except NotebookLMError as exc:
        print("Error de NotebookLM:\n", exc)
        return 1
    except Exception as exc:
        print("Error inesperado:\n", exc)
        return 2


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))

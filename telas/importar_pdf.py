"""Compatibilidade: encaminha para a nova tela de cadastro via PDF."""

from telas.cadastrar_questoes_via_pdf import (
    tela_cadastrar_questoes_via_pdf,
)


def tela_importar_pdf():
    tela_cadastrar_questoes_via_pdf()

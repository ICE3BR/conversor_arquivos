#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Arquivo principal que inicia a aplicação de conversão e compressão de arquivos
"""

import os
import sys

from interface.app import Application


def main():
    """
    Função principal que inicializa a aplicação
    """
    app = Application()
    app.mainloop()


if __name__ == "__main__":
    # Iniciar a aplicação
    main()

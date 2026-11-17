"""Gera o Pix "copia e cola" (BR Code estático) com o valor do pedido. Não depende do Django."""
import re
import unicodedata
from decimal import Decimal


def _campo(identificador, valor):
    return f"{identificador}{len(valor):02d}{valor}"


def _texto(valor, limite):
    """Remove acentos e símbolos (o padrão do Pix só aceita caracteres simples)."""
    sem_acento = unicodedata.normalize("NFKD", valor).encode("ascii", "ignore").decode()
    limpo = re.sub(r"[^A-Za-z0-9 ]", "", sem_acento).strip().upper()
    return limpo[:limite] or "NA"


def crc16(texto):
    """CRC16-CCITT (polinômio 0x1021, início 0xFFFF), exigido pelo padrão do Banco Central."""
    crc = 0xFFFF
    for byte in texto.encode():
        crc ^= byte << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) & 0xFFFF if crc & 0x8000 else (crc << 1) & 0xFFFF
    return f"{crc:04X}"


def montar_pix(chave, nome, cidade, valor, txid):
    """Devolve o texto do Pix copia e cola para `valor` reais."""
    conta = _campo("00", "br.gov.bcb.pix") + _campo("01", chave.strip())
    identificador = re.sub(r"[^A-Za-z0-9]", "", txid).upper()[:25] or "***"
    corpo = (
        _campo("00", "01")
        + _campo("01", "11")
        + _campo("26", conta)
        + _campo("52", "0000")
        + _campo("53", "986")
        + _campo("54", f"{Decimal(valor):.2f}")
        + _campo("58", "BR")
        + _campo("59", _texto(nome, 25))
        + _campo("60", _texto(cidade, 15))
        + _campo("62", _campo("05", identificador))
        + "6304"
    )
    return corpo + crc16(corpo)

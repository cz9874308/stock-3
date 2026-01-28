#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AES 加密解密工具模块

本模块提供了 AES（高级加密标准）算法的加密和解密功能，支持 CBC 和 ECB 两种模式，
以及多种填充方式。

核心概念
--------
- **AES**: 对称加密算法，密钥长度可为 128/192/256 位
- **CBC 模式**: 密码块链接模式，需要初始化向量（IV），安全性更高
- **ECB 模式**: 电子密码本模式，不需要 IV，但相同明文产生相同密文
- **填充模式**: 由于 AES 要求明文长度是 16 字节的倍数，需要对数据进行填充

支持的填充方式
--------------
- **NoPadding**: 不填充（要求数据长度已是 16 的倍数）
- **ZeroPadding**: 用 0x00 字节填充
- **PKCS5Padding**: PKCS#5 标准填充（与 PKCS7 相同）
- **PKCS7Padding**: PKCS#7 标准填充

使用方式
--------
加密示例::

    from Crypto.Cipher import AES
    from instock.lib.crypto_aes import AEScryptor

    key = b"maf45J8hg022yFsi"  # 16 字节密钥
    iv = b"0000000000000000"   # 16 字节 IV
    aes = AEScryptor(key, AES.MODE_CBC, iv, paddingMode="ZeroPadding")

    # 加密
    encrypted = aes.encryptFromString("Hello World")
    print(encrypted.toBase64())

    # 解密
    decrypted = aes.decryptFromBase64(encrypted.toBase64())
    print(decrypted.toString())

注意事项
--------
- 密钥长度必须是 16（AES-128）、24（AES-192）或 32（AES-256）字节
- CBC 模式下 IV 必须是 16 字节
- 生产环境中请勿使用示例中的固定密钥和 IV
"""

from typing import Optional

from Crypto.Cipher import AES
import base64
import binascii

__author__ = 'myh '
__date__ = '2023/3/10 '


class MData:
    """多格式数据容器类

    用于在不同数据格式（字符串、Base64、十六进制、二进制）之间进行转换。
    作为加密/解密操作的数据载体。

    Attributes:
        data: 内部存储的二进制数据
        characterSet: 字符编码，默认 UTF-8

    Example:
        >>> mdata = MData()
        >>> mdata.fromString("Hello")
        >>> print(mdata.toBase64())
        'SGVsbG8='
    """

    def __init__(self, data: bytes = b"", characterSet: str = 'utf-8'):
        """初始化数据容器

        Args:
            data: 初始二进制数据，默认为空
            characterSet: 字符编码，默认 UTF-8
        """
        self.data = data
        self.characterSet = characterSet

    def saveData(self, FileName: str) -> None:
        """将数据保存到文件

        Args:
            FileName: 目标文件路径
        """
        with open(FileName, 'wb') as f:
            f.write(self.data)

    def fromString(self, data: str) -> bytes:
        """从字符串加载数据

        Args:
            data: 输入字符串

        Returns:
            编码后的二进制数据
        """
        self.data = data.encode(self.characterSet)
        return self.data

    def fromBase64(self, data: str) -> bytes:
        """从 Base64 编码字符串加载数据

        Args:
            data: Base64 编码的字符串

        Returns:
            解码后的二进制数据
        """
        self.data = base64.b64decode(data.encode(self.characterSet))
        return self.data

    def fromHexStr(self, data: str) -> bytes:
        """从十六进制字符串加载数据

        Args:
            data: 十六进制字符串（如 "48656c6c6f"）

        Returns:
            解码后的二进制数据
        """
        self.data = binascii.a2b_hex(data)
        return self.data

    def toString(self) -> str:
        """将数据转换为字符串

        Returns:
            使用指定字符编码解码后的字符串
        """
        return self.data.decode(self.characterSet)

    def toBase64(self) -> str:
        """将数据转换为 Base64 编码字符串

        Returns:
            Base64 编码的字符串
        """
        return base64.b64encode(self.data).decode()

    def toHexStr(self) -> str:
        """将数据转换为十六进制字符串

        Returns:
            十六进制字符串
        """
        return binascii.b2a_hex(self.data).decode()

    def toBytes(self) -> bytes:
        """获取原始二进制数据

        Returns:
            内部存储的二进制数据
        """
        return self.data

    def __str__(self) -> str:
        """字符串表示

        尝试将数据解码为字符串，如果失败则返回 Base64 编码。
        """
        try:
            return self.toString()
        except Exception:
            return self.toBase64()


class AEScryptor:
    """AES 加密解密器

    提供 AES 算法的加密和解密功能，支持 CBC 和 ECB 模式，
    以及多种填充方式。

    Attributes:
        key: AES 密钥（16/24/32 字节）
        mode: 加密模式（AES.MODE_CBC 或 AES.MODE_ECB）
        iv: 初始化向量（CBC 模式需要，16 字节）
        characterSet: 字符编码
        paddingMode: 填充模式

    Example:
        >>> from Crypto.Cipher import AES
        >>> key = b"maf45J8hg022yFsi"
        >>> iv = b"0000000000000000"
        >>> aes = AEScryptor(key, AES.MODE_CBC, iv, paddingMode="PKCS7Padding")
        >>> encrypted = aes.encryptFromString("Secret Message")
        >>> decrypted = aes.decryptFromBase64(encrypted.toBase64())
        >>> print(decrypted)
        'Secret Message'
    """

    def __init__(
        self,
        key: bytes,
        mode: int,
        iv: bytes = b'',
        paddingMode: str = "NoPadding",
        characterSet: str = "utf-8"
    ):
        """初始化 AES 加密器

        Args:
            key: AES 密钥，必须是 16、24 或 32 字节
            mode: 加密模式，支持 AES.MODE_CBC 和 AES.MODE_ECB
            iv: 初始化向量，CBC 模式必须提供 16 字节的 IV
            paddingMode: 填充模式，可选值：
                - NoPadding: 不填充（数据长度需是 16 的倍数）
                - ZeroPadding: 用 0x00 填充
                - PKCS5Padding: PKCS#5 填充
                - PKCS7Padding: PKCS#7 填充
            characterSet: 字符编码，默认 UTF-8
        """
        self.key = key
        self.mode = mode
        self.iv = iv
        self.characterSet = characterSet
        self.paddingMode = paddingMode
        self.data = ""

    def __ZeroPadding(self, data: bytes) -> bytes:
        """Zero 填充：用 0x00 字节填充到 16 字节对齐"""
        data += b'\x00'
        while len(data) % 16 != 0:
            data += b'\x00'
        return data

    def __StripZeroPadding(self, data: bytes) -> bytes:
        """移除 Zero 填充"""
        data = data[:-1]
        while len(data) % 16 != 0:
            data = data.rstrip(b'\x00')
            if data[-1] != b"\x00":
                break
        return data

    def __PKCS5_7Padding(self, data: bytes) -> bytes:
        """PKCS5/PKCS7 填充：填充字节的值等于填充的长度"""
        needSize = 16 - len(data) % 16
        if needSize == 0:
            needSize = 16
        return data + needSize.to_bytes(1, 'little') * needSize

    def __StripPKCS5_7Padding(self, data: bytes) -> bytes:
        """移除 PKCS5/PKCS7 填充"""
        paddingSize = data[-1]
        return data.rstrip(paddingSize.to_bytes(1, 'little'))

    def __paddingData(self, data: bytes) -> bytes:
        """根据填充模式对数据进行填充"""
        if self.paddingMode == "NoPadding":
            if len(data) % 16 == 0:
                return data
            else:
                return self.__ZeroPadding(data)
        elif self.paddingMode == "ZeroPadding":
            return self.__ZeroPadding(data)
        elif self.paddingMode == "PKCS5Padding" or self.paddingMode == "PKCS7Padding":
            return self.__PKCS5_7Padding(data)
        else:
            print("不支持Padding")

    def __stripPaddingData(self, data: bytes) -> bytes:
        """根据填充模式移除数据的填充"""
        if self.paddingMode == "NoPadding":
            return self.__StripZeroPadding(data)
        elif self.paddingMode == "ZeroPadding":
            return self.__StripZeroPadding(data)
        elif self.paddingMode == "PKCS5Padding" or self.paddingMode == "PKCS7Padding":
            return self.__StripPKCS5_7Padding(data)
        else:
            print("不支持Padding")

    def setCharacterSet(self, characterSet: str) -> None:
        """设置字符编码

        Args:
            characterSet: 字符编码名称（如 'utf-8', 'gbk'）
        """
        self.characterSet = characterSet

    def setPaddingMode(self, mode: str) -> None:
        """设置填充模式

        Args:
            mode: 填充模式，可选值：NoPadding, ZeroPadding, PKCS5Padding, PKCS7Padding
        """
        self.paddingMode = mode

    def decryptFromBase64(self, entext: str) -> MData:
        """从 Base64 编码的密文进行 AES 解密

        Args:
            entext: Base64 编码的密文字符串

        Returns:
            包含解密后明文的 MData 对象

        Example:
            >>> decrypted = aes.decryptFromBase64("SGVsbG8gV29ybGQ=")
            >>> print(decrypted.toString())
        """
        mData = MData(characterSet=self.characterSet)
        self.data = mData.fromBase64(entext)
        return self.__decrypt()

    def decryptFromHexStr(self, entext: str) -> MData:
        """从十六进制字符串密文进行 AES 解密

        Args:
            entext: 十六进制编码的密文字符串

        Returns:
            包含解密后明文的 MData 对象
        """
        mData = MData(characterSet=self.characterSet)
        self.data = mData.fromHexStr(entext)
        return self.__decrypt()

    def decryptFromString(self, entext: str) -> MData:
        """从字符串密文进行 AES 解密

        Args:
            entext: 密文字符串

        Returns:
            包含解密后明文的 MData 对象
        """
        mData = MData(characterSet=self.characterSet)
        self.data = mData.fromString(entext)
        return self.__decrypt()

    def decryptFromBytes(self, entext: bytes) -> MData:
        """从二进制密文进行 AES 解密

        Args:
            entext: 二进制密文数据

        Returns:
            包含解密后明文的 MData 对象
        """
        self.data = entext
        return self.__decrypt()

    def encryptFromString(self, data: str) -> MData:
        """对字符串进行 AES 加密

        Args:
            data: 待加密的明文字符串

        Returns:
            包含加密后密文的 MData 对象，可通过 toBase64()、toHexStr() 等方法输出

        Example:
            >>> encrypted = aes.encryptFromString("Hello World")
            >>> print(encrypted.toBase64())
        """
        self.data = data.encode(self.characterSet)
        return self.__encrypt()

    def __encrypt(self) -> Optional[MData]:
        """执行 AES 加密（内部方法）"""
        if self.mode == AES.MODE_CBC:
            aes = AES.new(self.key, self.mode, self.iv)
        elif self.mode == AES.MODE_ECB:
            aes = AES.new(self.key, self.mode)
        else:
            print("不支持这种模式")
            return

        data = self.__paddingData(self.data)
        enData = aes.encrypt(data)
        return MData(enData)

    def __decrypt(self) -> Optional[MData]:
        """执行 AES 解密（内部方法）"""
        if self.mode == AES.MODE_CBC:
            aes = AES.new(self.key, self.mode, self.iv)
        elif self.mode == AES.MODE_ECB:
            aes = AES.new(self.key, self.mode)
        else:
            print("不支持这种模式")
            return
        data = aes.decrypt(self.data)
        mData = MData(self.__stripPaddingData(data), characterSet=self.characterSet)
        return mData


if __name__ == '__main__':
    key = b"maf45J8hg022yFsi"
    iv = b"0000000000000000"
    aes = AEScryptor(key, AES.MODE_CBC, iv, paddingMode="ZeroPadding", characterSet='utf-8')

    data = "8888888888888888"
    rData = aes.encryptFromString(data)
    print("密文：", rData.toBase64())
    rData = aes.decryptFromBase64(rData.toBase64())
    print("明文：", rData)

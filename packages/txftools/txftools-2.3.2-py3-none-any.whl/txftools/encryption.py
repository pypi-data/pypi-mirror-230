# pip install pycryptodomex
# pip install rsa
from Cryptodome.Cipher import AES, DES3
import base64
import os
import rsa  # 4.9
import os
from Cryptodome.Util import number
from Cryptodome import Random
from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
import base64


class AESDecodeEncode(object):
    """aes 加密"""
    key = '0CoJUm6Qyw8W8jud'
    vi = '0102030405060708'

    @classmethod
    def set_aes(cls, key=None, data=None, vi=None):
        key = key or cls.key
        vi = vi or cls.vi
        pad = lambda s: s + (16 - len(s) % 16) * chr(16 - len(s) % 16)
        data = pad(data)
        cipher = AES.new(key.encode('utf8'), AES.MODE_CBC, vi.encode('utf8'))
        encrypted_bytes = cipher.encrypt(data.encode('utf8'))
        bs64_strs = base64.b64encode(encrypted_bytes)  # type byte
        ret = bs64_strs.decode('utf8')
        return ret

    @classmethod
    def get_aes(cls, key, data, vi):
        key = key or cls.key
        vi = vi or cls.vi
        data = data.encode('utf8')
        encode_bytes = base64.decodebytes(data)
        cipher = AES.new(key.encode('utf8'), AES.MODE_CBC, vi.encode('utf8'))
        text_decrypted = cipher.decrypt(encode_bytes)
        unpad = lambda s: s[0:-s[-1]]
        text_decrypted = unpad(text_decrypted)
        text_decrypted = text_decrypted.decode('utf8')
        return text_decrypted

    def execute_demo(self):
        # aesde = AESDecodeEncode
        # key = '0CoJUm6Qyw8W8jud'  # 自己密钥
        # data = 'sdadsdsdsfd'  # 需要加密的内容
        # vi = '0102030405060708'
        # enctext = aesde.set_aes(key, data)
        # print(enctext)
        # text_decrypted = get_aes(key, enctext)
        # print(text_decrypted)
        pass


class DES3ECBDecodeEncode(object):
    # 加密模式为 ECB
    def __init__(self, key, encode_text=None, decode_text=None, is_bs64=False):
        """
        :param key:          b'4J6r0E4406Uo3eo0D182wH5G'
        :param encode_text:  Python rocks!
        :param decode_text:  b'@\xa9\n\xfaa\xcc\xd5\x8f\xf8V}5H\x08zC'
        """
        self.key = key
        self.encode_text = encode_text
        self.is_bs64 = is_bs64
        self.decode_text = decode_text
        self.des = DES3.new(self.key, DES3.MODE_ECB)  # 创建一个DES实例

    def pad(self):
        text = self.encode_text
        while len(text) % 8 != 0:
            text += ' '
        return text

    def encode_des3_data(self):
        pad_text = self.pad()

        encode_text = self.des.encrypt(pad_text.encode('utf-8'))  # 加密
        if self.is_bs64:
            encode_text = base64.b64encode(encode_text)
        return encode_text

    def decode_des3_data(self):
        decode_text = self.decode_text
        if self.is_bs64:
            decode_text = base64.b64decode(decode_text)
        return self.des.decrypt(decode_text).decode().rstrip(' ')  # 解密

    def execute_demo(self):
        """
        key = b'4J6r0E4406Uo3eo0D182wH5G'
        text = 'Python rocks!'
        v = DES3DecodeEncode(key=key, encode_text=text, decode_text=b'@\xa9\n\xfaa\xcc\xd5\x8f\xf8V}5H\x08zC', is_bs64=False)
        ed = v.encode_des3_data()
        print(ed)
        dd = v.decode_des3_data()
        print(dd)
        """
        pass


class RSADecodeEncode(object):
    """目前只支持 自己生成的
    BEGIN RSA PRIVATE KEY 格式
    """

    def __init__(self, pubkey_path=None, pri_path=None):
        self.pub_path = pubkey_path or str(os.getcwd()) + '/pub_key.txt'
        self.pri_path = pri_path or str(os.getcwd()) + '/pri_key.txt'

    def set_pubkey_privkey(self, nbits=1024):
        pubkey, privkey = rsa.newkeys(nbits)
        return pubkey, privkey

    def save_keys(self, pubkey, privkey):
        """
        public_key_bytes
                -----BEGIN RSA PUBLIC KEY-----
                MIIBCgKCAQEAh151YMf/6i.........
                -----END RSA PUBLIC KEY-----

        private_key_bytes
                -----BEGIN RSA PRIVATE KEY-----
                MIIEqAIBAAKCAQEAhl4lYMf/6iW6wXHa8BJs5DPPX20azt3hCzZvI85/G/aoNhbY
                1AApA..............
                -----END RSA PRIVATE KEY-----
                """
        public_key_bytes, private_key_bytes = pubkey.save_pkcs1(), privkey.save_pkcs1()
        with open(self.pub_path, 'wb') as f:
            f.write(public_key_bytes)

        with open(self.pri_path, 'wb') as f:
            f.write(private_key_bytes)
        return pubkey, privkey

    def handle_pub_key(self, key):
        """
        处理公钥
        公钥格式pem，处理成以-----BEGIN PUBLIC KEY-----开头，-----END PUBLIC KEY-----结尾的格式
        :param key:pem格式的公钥，无-----BEGIN PUBLIC KEY-----开头，-----END PUBLIC KEY-----结尾
        :return:
        """
        start = '-----BEGIN PUBLIC KEY-----\n'
        end = '-----END PUBLIC KEY-----'
        result = ''
        # 分割key，每64位长度换一行
        divide = int(len(key) / 64)
        divide = divide if (divide > 0) else divide + 1
        line = divide if (len(key) % 64 == 0) else divide + 1
        for i in range(line):
            result += key[i * 64:(i + 1) * 64] + '\n'
        result = start + result + end
        return result

    def handle_pri_key(self, pri_key):
        return self.handle_pub_key(pri_key)

    def format_pub_key(self, pubkey_path=None, pub_key=None):
        if not pub_key:
            with open(pubkey_path or self.pub_path, 'rb') as f:
                pub_data = f.read()
                pub_key = rsa.PublicKey.load_pkcs1(pub_data)
        else:
            pub_key = self.handle_pub_key(pub_key)
            pub_key = rsa.PublicKey.load_pkcs1_openssl_pem(pub_key)
        return pub_key

    def format_pri_key(self, pri_path=None, pri_key=None):
        if not pri_key:
            with open(pri_path or self.pri_path, 'rb') as f:
                pri_data = f.read()
                pri_key = rsa.PrivateKey.load_pkcs1(pri_data)
        else:
            pri_key = self.handle_pri_key(pri_key)
            pri_key = rsa.PublicKey.load_pkcs1_openssl_pem(pri_key)
        return pri_key

    def set_ras(self, message, pubkey_path=None, pub_key=None):
        pub_key = self.format_pub_key(pubkey_path, pub_key=pub_key)

        crypto = b''
        divide = int(len(message) / 117)
        divide = divide if (divide > 0) else divide + 1
        line = divide if (len(message) % 117 == 0) else divide + 1

        get_len = ''
        for i in range(line):
            v = rsa.encrypt(message[i * 117:(i + 1) * 117].encode(), pub_key)
            crypto += v
            if not get_len:
                get_len = len(v)
        crypto1 = base64.b64encode(crypto)
        return crypto1.decode('utf-8'), get_len

    def decode_message_type(self, message):
        if isinstance(message, str):
            return base64.b64decode(message)
        elif isinstance(message, bytes):
            return message
        else:
            raise ValueError('你的类型我无法确定')

    def get_ras(self, message, pri_path=None, pri_key=None, get_len=None):
        if not get_len:
            get_len = 128
        message = self.decode_message_type(message)
        pri_key = self.format_pri_key(pri_path, pri_key)
        crypto = b''
        divide = int(len(message) / get_len)
        divide = divide if (divide > 0) else divide + 1
        line = divide if (len(message) % get_len == 0) else divide + 1
        for i in range(line):
            decode_text = message[i * get_len:(i + 1) * get_len]
            crypto += rsa.decrypt(decode_text, pri_key)

        return crypto.decode()


class Pkcs8RSAEncodeDecode(object):
    """
    JAVA与Python代码，可以实现JAVA生成公钥密钥，JAVA用公钥解密，Python用私钥解密，反之亦可。
    Python要注意设置私钥格式pkcs8，默认是pkcs1。为了和JAVA互用，这里设置格式为pkcs8

    java code :
    import javax.crypto.Cipher;
    import javax.crypto.NoSuchPaddingException;
    import java.io.ByteArrayOutputStream;
    import java.io.UnsupportedEncodingException;
    import java.nio.charset.StandardCharsets;
    import java.security.InvalidKeyException;
    import java.security.KeyFactory;
    import java.security.KeyPair;
    import java.security.KeyPairGenerator;
    import java.security.NoSuchAlgorithmException;
    import java.security.PrivateKey;
    import java.security.PublicKey;
    import java.security.spec.PKCS8EncodedKeySpec;
    import java.security.interfaces.RSAPrivateKey;
    import java.security.interfaces.RSAPublicKey;
    import java.security.spec.InvalidKeySpecException;
    import java.security.spec.KeySpec;
    import java.security.spec.X509EncodedKeySpec;
    import java.util.Base64;

    public class RSAUtil extends AbstractCrypto {
        private static final String RSA_ALGORITHM = "RSA";
        private static final int RSA_2048 = 2048;

        public void generateSecret() throws Exception {
            KeyPairGenerator keyPairGenerator = KeyPairGenerator.getInstance(RSA_ALGORITHM);
            keyPairGenerator.initialize(RSA_2048);
            KeyPair keyPair = keyPairGenerator.generateKeyPair();
            PublicKey publicKey = keyPair.getPublic();
            PrivateKey privateKey = keyPair.getPrivate();

            String publicKeyString = Base64.getEncoder().encodeToString(publicKey.getEncoded());
            System.out.println("public key string: " + publicKeyString);

            String privateKeyString = Base64.getEncoder().encodeToString(privateKey.getEncoded());
            System.out.println("private key String: " + privateKeyString);
        }

        public String encrypt(String plaintext, String key) throws Exception {
            return publicKeyEncrypted(plaintext, key);
        }

        public String decrypt(String ciphertext, String key) throws Exception {
            return privateDecrypt(ciphertext, key);
        }

        public String publicKeyEncrypted(String plaintext, String publicKeyString) throws NoSuchAlgorithmException, NoSuchPaddingException, InvalidKeyException, InvalidKeySpecException {
            RSAPublicKey publicKey = getPublicKey(publicKeyString);
            Cipher cipher = Cipher.getInstance(RSA_ALGORITHM);
            cipher.init(Cipher.ENCRYPT_MODE, publicKey);
            return Base64.getEncoder().encodeToString(rsaCodec(cipher, plaintext.getBytes(StandardCharsets.UTF_8), publicKey.getModulus().bitLength() / 8 - 11));
        }

        private RSAPublicKey getPublicKey(String publicKeyString) throws NoSuchAlgorithmException, InvalidKeySpecException {
            KeyFactory keyFactory = KeyFactory.getInstance(RSA_ALGORITHM);
            KeySpec keySpec = new X509EncodedKeySpec(Base64.getDecoder().decode(publicKeyString));
            return (RSAPublicKey) keyFactory.generatePublic(keySpec);
        }

        private static RSAPrivateKey getPrivateKey(String privateKeyString) throws NoSuchAlgorithmException, InvalidKeySpecException {
            KeyFactory keyFactory = KeyFactory.getInstance(RSA_ALGORITHM);
            KeySpec pkcS8EncodedKeySpec = new PKCS8EncodedKeySpec(Base64.getDecoder().decode(privateKeyString));
            return (RSAPrivateKey) keyFactory.generatePrivate(pkcS8EncodedKeySpec);
        }

        public static String privateDecrypt(String ciphertext, String privateKeyString) throws NoSuchAlgorithmException, InvalidKeySpecException, NoSuchPaddingException, InvalidKeyException, UnsupportedEncodingException {
            RSAPrivateKey privateKey = getPrivateKey(privateKeyString);

            Cipher cipher = Cipher.getInstance(RSA_ALGORITHM);
            cipher.init(Cipher.DECRYPT_MODE, privateKey);
            return new String(
                    rsaCodec(cipher, Base64.getDecoder().decode(ciphertext), privateKey.getModulus().bitLength() / 8), StandardCharsets.UTF_8
            );
        }

        private static byte[] rsaCodec(Cipher cipher, byte[] data, int maxBlock) {
            int offset = 0;
            byte[] buffer;
            int i = 0;

            try (ByteArrayOutputStream byteArrayOutputStream = new ByteArrayOutputStream()) {
                while (data.length > offset) {
                    if (data.length - offset > maxBlock) {
                        buffer = cipher.doFinal(data, offset, maxBlock);
                    } else {
                        buffer = cipher.doFinal(data, offset, data.length - offset);
                    }
                    byteArrayOutputStream.write(buffer, 0, buffer.length);
                    i++;
                    offset = i * maxBlock;
                }
                return byteArrayOutputStream.toByteArray();
            } catch (Exception e) {
                throw new RuntimeException(e);
            }
        }

    }

    """

    encoding_utf8 = 'utf-8'
    PRIVATE_KEY_BEGIN = '-----BEGIN PRIVATE KEY-----'
    PRIVATE_KEY_END = '-----END PRIVATE KEY-----'
    PUBLIC_KEY_BEGIN = '-----BEGIN PUBLIC KEY-----'
    PUBLIC_KEY_END = '-----END PUBLIC KEY-----'
    key_path_ = os.getcwd()
    print(key_path_)

    def rsa_create_key(self, bits=1024, key_path=None, is_save=True):
        key_path = key_path or self.key_path_
        random_generator = Random.new().read
        rsa = RSA.generate(bits, random_generator)
        pkcs8_private_key = rsa.exportKey(format='PEM', passphrase=None, pkcs=8, protection=None)
        private_key_with_title_and_bottom = pkcs8_private_key.decode("utf-8")
        private_key_string = private_key_with_title_and_bottom.removeprefix(self.PRIVATE_KEY_BEGIN) \
            .removesuffix(self.PRIVATE_KEY_END).replace('\n', "")
        public_pem = rsa.publickey().exportKey()
        public_key_with_begin_and_end = public_pem.decode(self.encoding_utf8)
        public_key_string = public_key_with_begin_and_end.removeprefix(self.PUBLIC_KEY_BEGIN) \
            .removesuffix(self.PUBLIC_KEY_END).replace("\n", "")

        if is_save:
            with open(key_path + '/rsa_pkcs8.pri', 'wb') as f:
                f.write(private_key_string.encode(self.encoding_utf8))

            with open(key_path + '/rsa_pkcs8.pub', 'wb') as f:
                f.write(public_key_string.encode(self.encoding_utf8))

        print('public_key_string')
        print(public_key_string)
        print('=' * 20)
        print('private_key_string')
        print(private_key_string)
        print('-' * 20)
        return public_key_string, private_key_string

    def rsa_public_key_encrypt(self, plaintext, pub_path=None, public_key=None):
        if not public_key:
            key_path = pub_path or self.key_path_
            pub_key_file = key_path + '/pkcs8.pub'
            with open(pub_key_file, 'rb') as f:
                pri_key_string = f.read()
            rsa_key = RSA.importKey(base64.b64decode(pri_key_string))
        else:
            rsa_key = RSA.importKey(base64.b64decode(public_key))
        cipher = Cipher_pkcs1_v1_5.new(rsa_key)

        max_block = int(number.size(rsa_key.n) / 8 - 11)
        length = len(plaintext)
        offset = 0
        res = []
        plaintext_bytes = plaintext.encode(self.encoding_utf8)
        while length - offset > 0:
            if length - offset > max_block:
                res.append(cipher.encrypt(plaintext_bytes[offset:offset + max_block]))
            else:
                res.append(cipher.encrypt(plaintext_bytes[offset:]))
            offset += max_block

        cipher_text = base64.b64encode(b''.join(res))
        return cipher_text.decode(self.encoding_utf8)

    def rsa_private_key_decrypt(self, cipher_text, key_path=None, private_key=None):
        if not private_key:
            key_path = key_path or self.key_path_
            pri_key_file = key_path + '/pkcs8.pri'
            with open(pri_key_file, 'rb') as f:
                private_key_string = f.read()
            private_key = RSA.importKey(base64.b64decode(private_key_string))
        else:
            private_key = RSA.importKey(base64.b64decode(private_key))

        cipher = Cipher_pkcs1_v1_5.new(private_key)

        block_size = int(number.size(private_key.n) / 8)
        cipher_text_bytes = base64.b64decode(cipher_text)
        length = len(cipher_text_bytes)
        offset = 0
        res = []

        while length - offset > 0:
            if length - offset > block_size:
                res.append(cipher.decrypt(cipher_text_bytes[offset: offset + block_size], "ERROR"))
            else:
                res.append(cipher.decrypt(cipher_text_bytes[offset:], "ERROR"))
            offset += block_size

        plaintext = b''.join(res)
        return plaintext.decode(self.encoding_utf8)

    def execute_demo(self):
        """
        p8_rsaed = Pkcs8RSAEncodeDecode()
        public_key_string, private_key_string = p8_rsaed.rsa_create_key()
        plaintext = '莫问前程'
        ed = p8_rsaed.rsa_public_key_encrypt(plaintext, pub_path=None, public_key=public_key_string)
        dd = p8_rsaed.rsa_private_key_decrypt(cipher_text=ed, key_path=None, private_key=private_key_string)

        public_key_string, private_key_string = 'MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDQWdhR7hBm+h6a0s1GJIS9nAZIoZUtTaf1HkPTw5hWlEsuesIqpy2rhckkb1VK044S7/hSnmXb+ydqf6TZPTft+IWhImqyFLh1wcF6mHWx9gfeW29Ewkl/ksegnOP83UcNNTtJPs+yyVNsLOFrVzdDSK4rKwjZgGnRyPY4wYVOowIDAQAB', 'MIICdwIBADANBgkqhkiG9w0BAQEFAASCAmEwggJdAgEAAoGBANBZ2FHuEGb6HprSzUYkhL2cBkihlS1Np/UeQ9PDmFaUSy56wiqnLauFySRvVUrTjhLv+FKeZdv7J2p/pNk9N+34haEiarIUuHXBwXqYdbH2B95bb0TCSX+Sx6Cc4/zdRw01O0k+z7LJU2ws4WtXN0NIrisrCNmAadHI9jjBhU6jAgMBAAECgYA2XctZjaJQDKIhyjHwRKUyiN0G5Mr1WFckWfJe9qHwrZ90kGnMEXWUVUOoMzjxXoSrIl0MyfJQVZfybT5JxXSrNm+44umj6jhkx+U3Zzwm96FhDDHVjIpYqW+x4gEVaVHMNTkXMKrH5iGK0g/YRHuDBKuoQTw0NkKCKB3LKQ7RaQJBAOX/GOm+DNHlQ4f8oC/rnnA+bAdAdIHJlZUurS1wG/71VRAK+8OxIl2XdUJCpTUA5HRpBTFAE4nE2v7pZZyRLr0CQQDn6EAtQmv9BAr8OlE/XSYLKdPZW1KiUIBZ9ND6rE8CxIuf4JydiRx+0HGs61remMKOSm8PcFbo76hSnwBmiXjfAkAiac8CemtUpKc8G7KkOO8WAGENnLlSCiWVksxatiGaPn8hzWLqXwCzXEwxQ+OQULfeKzCZs+q4fHoAFlAb4yVJAkEA4d7UewCBm0pPxMCsF5ILFr5jhwUqY8sSaAtJa41d2y1BbLNg9xLvPRiaTzhgJgQVIm+e4iOhknixsd8JjdUBcwJBALPeBUGdxvVPmHcZzBYmRCB7afqw1nh2AYCBGpIETmJiCxGfKcK41Ra0G5gUECCetUPjgimailivtu4hSzhkEH8='
        plaintext = '莫问前程'
        ed = p8_rsaed.rsa_public_key_encrypt(plaintext, pub_path=None)
        dd = p8_rsaed.rsa_private_key_decrypt(cipher_text=ed, key_path=None)
        """
        pass


def set_pri_pub_pkcs8(bits=1024, key_path=None, is_save=None):
    pub_key_str, pri_key_str = Pkcs8RSAEncodeDecode().rsa_create_key(bits, key_path, is_save)
    return pub_key_str, pri_key_str


def get_rsa_pkcs8(cipher_text, key_path=None, private_key_string=None):
    dd = Pkcs8RSAEncodeDecode().rsa_private_key_decrypt(cipher_text=cipher_text, key_path=key_path,
                                                        private_key=private_key_string)
    return dd


def set_rsa_pkcs8(plaintext, pub_path=None, public_key_string=None):
    ed = Pkcs8RSAEncodeDecode().rsa_public_key_encrypt(plaintext, pub_path=pub_path, public_key=public_key_string)
    return ed


def set_des3_ecd(key, encode_text, is_bs64=True):
    """
    返回的数据 如果是bs64的 is_bs64=True 反之
    """
    v = DES3ECBDecodeEncode(key=key, encode_text=encode_text, is_bs64=is_bs64)
    ed = v.encode_des3_data()
    return ed


def get_des3_ecd(key, decode_text, is_bs64=True):
    """
    decode_text  如果是bs64的 is_bs64=True 反之
    """
    v = DES3ECBDecodeEncode(key=key, decode_text=decode_text, is_bs64=is_bs64)
    dd = v.decode_des3_data()
    return dd


def set_aes(key, source_str, vi):
    """
    # 密钥（key）, 密斯偏移量（iv）
    source_str  str 此参数是生成 aes的参数，此参数如果有值就直接加密
    """
    return AESDecodeEncode().set_ret(key, source_str, vi)


def get_aes(key, source_str, vi):
    # 密钥（key）, 密斯偏移量（iv）
    return AESDecodeEncode().get_aes(key, source_str, vi)


def rsa_save_pub_pri_key(nbits=1024, pubkey_path=None, pri_path=None):
    r = RSADecodeEncode(pubkey_path, pri_path)
    pubkey, privkey = r.set_pubkey_privkey(nbits=nbits)
    RSADecodeEncode().save_keys(pubkey, privkey)


def set_rsa(message, pubkey_path, len_=False):
    r = RSADecodeEncode()
    ret, get_len = r.set_ras(message, pubkey_path)
    if len_:
        return ret, get_len
    return ret


def get_rsa(message, pri_path, get_len=None):
    r = RSADecodeEncode()
    ret = r.get_ras(message, pri_path, get_len)
    return ret



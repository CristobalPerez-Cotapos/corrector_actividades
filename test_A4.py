import unittest
from encriptar import serializar_diccionario, verificar_secuencia, \
    codificar_secuencia, codificar_largo, separar_msg, encriptar
from desencriptar import deserializar_diccionario, decodificar_largo, \
    separar_msg_encriptado, decodificar_secuencia, desencriptar
from errors import JsonError, SequenceError
from io import StringIO
from unittest.mock import patch


class TestEncriptar(unittest.TestCase):

    def test_serializar_diccionario(self):
        test = serializar_diccionario({"1": [1, 5], "2": "aei"})
        res = bytearray(b'{"1": [1, 5], "2": "aei"}')

        # Verificar tipo de dato pedido
        self.assertIsInstance(test, bytearray)
        # Verificar resultados
        self.assertEqual(test, res)
        self.assertEqual(test, res)

    def test_serializar_diccionario_excepcion(self):
        # Verificar que lavanta excepcion
        no_serializable = {"anya": set()}
        self.assertRaises(JsonError, serializar_diccionario, no_serializable)

        # Verificar que no levanta excepcion
        serializable = {"anya": "as"}
        try:
            serializar_diccionario(serializable)
        except:
            self.fail(
                "Se levantó una excepción con un input que si se puede serializar")

    def test_verificar_secuencia(self):
        mensaje = bytearray(b'\x00\x01\x02\x09')
        self.assertRaises(SequenceError, verificar_secuencia, mensaje, [2000])
        self.assertRaises(SequenceError, verificar_secuencia, mensaje, [1, 1])
        # Verificar que retorne None cuando todo es válido
        self.assertIsNone(verificar_secuencia(mensaje, [1, 2]))

    def test_codificar_secuencia(self):
        test_1 = codificar_secuencia([1, 2, 3])
        res_1 = bytearray(b'\x00\x01\x00\x02\x00\x03')
        # Verificar tipo de dato pedido
        self.assertIsInstance(test_1, bytearray)
        # Verificar resultados
        self.assertEqual(test_1, res_1)

    def test_codificar_secuencia_2(self):
        test_2 = codificar_secuencia([11, 4242, 12])
        res_2 = bytearray(b'\x00\x0b\x10\x92\x00\x0c')
        # Verificar tipo de dato pedido
        self.assertIsInstance(test_2, bytearray)
        # Verificar resultados
        self.assertEqual(test_2, res_2)

    def test_codificar_largo(self):
        test_1 = codificar_largo(7)
        res_1 = bytearray(b'\x00\x00\x00\x07')
        # Verificar tipo de dato pedido
        self.assertIsInstance(test_1, bytearray)
        # Verificar resultados
        self.assertEqual(test_1, res_1)

    def test_codificar_largo_2(self):
        test_2 = codificar_largo(4241)
        res_2 = bytearray(b'\x00\x00\x10\x91')
        # Verificar tipo de dato pedido
        self.assertIsInstance(test_2, bytearray)
        # Verificar resultados
        self.assertEqual(test_2, res_2)

    def test_separar_msg(self):
        test_1 = separar_msg(bytearray(b'\x00\x01\x02\x03'), [1, 3])
        res_1 = [bytearray(b'\x01\x03'), bytearray(b'\x00\x02')]
        # Verificar tipo de dato pedido
        self.assertIsInstance(res_1, list)
        # Verificar resultados
        self.assertListEqual(test_1, res_1)

    def test_separar_msg_2(self):
        test_2 = separar_msg(bytearray(b'\x00\x01\x02\x03'), [3, 1])
        res_2 = [bytearray(b'\x03\x01'), bytearray(b'\x00\x02')]
        # Verificar tipo de dato pedido
        self.assertIsInstance(res_2, list)
        # Verificar resultados
        self.assertListEqual(test_2, res_2)

    def test_encriptar(self):
        test_1 = encriptar(bytearray(b'\x00\x01\x02\x03\x05'), [1, 3])
        res_1 = bytearray(b'\x00\x00\x00\x02\x01\x03\x00\x02\x05\x00\x01\x00\x03')
        # Verificar tipo de dato pedido
        self.assertIsInstance(res_1, bytearray)
        # Verificar resultados
        self.assertEqual(test_1, res_1)

    def test_encriptar_2(self):
        test_2 = encriptar(bytearray(b'\x10\x01\x02\x03\xAA'), [1, 0])
        res_2 = bytearray(b'\x00\x00\x00\x02\x01\x10\x02\x03\xaa\x00\x01\x00\x00')
        # Verificar tipo de dato pedido
        self.assertIsInstance(res_2, bytearray)
        # Verificar resultados
        self.assertEqual(test_2, res_2)


class TestDesencriptar(unittest.TestCase):
    def test_deserializar_diccionario(self):
        test = deserializar_diccionario(bytearray(b'{"1": [1, 5], "2": "aei"}'))
        res = {"1": [1, 5], "2": "aei"}

        # Verificar tipo de dato pedido
        self.assertIsInstance(test, dict)
        # Verificar resultados
        self.assertDictEqual(test, res)

    def test_deserializar_diccionario_excepcion(self):
        # Verificar que lavanta excepcion
        no_deserializable = b'{123:}'
        self.assertRaises(JsonError, deserializar_diccionario, no_deserializable)

        # Verificar que no levanta excepcion
        desserializable = bytearray(b'{"user": "name"}')
        try:
            deserializar_diccionario(desserializable)
        except:
            self.fail("Se levantó una excepción con un input que si se puede deserializar")

    def test_decodificar_largo(self):
        test_1 = decodificar_largo(bytearray(b'\x00\x00\x00\x02'))
        res_1 = 2
        # Verificar tipo de dato pedido
        self.assertIsInstance(test_1, int)
        # Verificar resultados
        self.assertEqual(test_1, res_1)

    def test_decodificar_largo_2(self):
        test_2 = decodificar_largo(bytearray(b'\xA0\xA0\x11\xA1'))
        res_2 = 2694844833
        # Verificar tipo de dato pedido
        self.assertIsInstance(test_2, int)
        # Verificar resultados
        self.assertEqual(test_2, res_2)

    def test_separar_msg_encriptado(self):
        test_1 = separar_msg_encriptado(
            bytearray(b'\x00\x00\x00\x02\x01\x03\x00\x02\x08\x00\x01\x00\x03'))

        res_1 = [bytearray(b'\x01\x03'), bytearray(
            b'\x00\x02\x08'), bytearray(b'\x00\x01\x00\x03')]
        # Verificar tipo de dato pedido
        self.assertIsInstance(res_1, list)
        # Verificar resultados
        self.assertListEqual(test_1, res_1)

    def test_separar_msg_encriptado_2(self):
        test_2 = separar_msg_encriptado(
            bytearray(b'\x00\x00\x00\x01\x05\x00\x01\x02\xAA\x00\x03'))
        res_2 = [bytearray(b'\x05'), bytearray(
            b'\x00\x01\x02\xAA'), bytearray(b'\x00\x03')]
        # Verificar tipo de dato pedido
        self.assertIsInstance(res_2, list)
        # Verificar resultados
        self.assertListEqual(test_2, res_2)

    def test_decodificar_secuencia(self):
        test_1 = decodificar_secuencia(bytearray(b'\x00\x01\x00\x02\x00\x03'))
        res_1 = [1, 2, 3]
        # Verificar tipo de dato pedido
        self.assertIsInstance(res_1, list)
        # Verificar resultados
        self.assertListEqual(test_1, res_1)

    def test_decodificar_secuencia_2(self):
        test_2 = decodificar_secuencia(bytearray(b'\x00\x0b\x10\x92\x00\x0b'))
        res_2 = [11, 4242, 11]
        # Verificar tipo de dato pedido
        self.assertIsInstance(res_2, list)
        # Verificar resultados
        self.assertListEqual(test_2, res_2)

    def test_desencriptar(self):
        test_1 = desencriptar(
            bytearray(b'\x00\x00\x00\x02\x01\x03\x00\x02\x05\x00\x01\x00\x03'))
        test_2 = desencriptar(
            bytearray(b'\x00\x00\x00\x01\x03\x00\x01\x02\xAA\x00\x03'))
        res_1 = bytearray(b'\x00\x01\x02\x03\x05')
        res_2 = bytearray(b'\x00\x01\x02\x03\xAA')

        # Verificar tipo de dato pedido
        self.assertIsInstance(res_1, bytearray)
        # Verificar resultados
        self.assertEqual(test_1, res_1)
        self.assertEqual(test_2, res_2)

    def test_desencriptar_2(self):
        test_1 = desencriptar(
            bytearray(b'\x00\x00\x00\x04abcdefghijklmn\x00\x02\x00\x03\x00\n\x00\x0c'))
        test_2 = desencriptar(bytearray(
            b'\x00\x00\x00\x05mata123\x00\x02\x00\x01\x00\x00\x00\x03\x00\x04'))
        res_1 = bytearray(b'efabghijklcmdn')
        res_2 = bytearray(b'tama123')

        # Verificar tipo de dato pedido
        self.assertIsInstance(res_1, bytearray)
        # Verificar resultados
        self.assertEqual(test_1, res_1)
        self.assertEqual(test_2, res_2)


if __name__ == '__main__':
    with patch('sys.stdout', new=StringIO()):
        unittest.main(verbosity=2)

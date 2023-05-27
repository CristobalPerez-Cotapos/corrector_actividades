from carrera import Carrera, Corredor
import unittest
from unittest.mock import patch
from io import StringIO
from threading import Event, Thread
import signal
from functools import wraps


class TimeoutError(AssertionError):

    """Thrown when a timeout occurs in the `timeout` context manager."""

    def __init__(self, value="Timed Out"):
        self.value = value

    def __str__(self):
        return repr(self.value)


def timeout(seconds=None):
    def decorate(function):
        def handler(signum, frame):
            raise TimeoutError("Timeout")

        @wraps(function)
        def new_function(*args, **kwargs):
            new_seconds = kwargs.pop('timeout', seconds)
            if new_seconds:
                old = signal.signal(signal.SIGALRM, handler)
                signal.setitimer(signal.ITIMER_REAL, new_seconds)

            if not seconds:
                return function(*args, **kwargs)

            try:
                return function(*args, **kwargs)
            finally:
                if new_seconds:
                    signal.setitimer(signal.ITIMER_REAL, 0)
                    signal.signal(signal.SIGALRM, old)
        return new_function

    return decorate


N_SECOND = 0.2


class FakeLock:

    def __init__(self) -> None:
        self._locked = False
        self.accessed = False
        self.blocking = True
        self.dueño = None

    def acquire(self, blocking=True):
        try:
            self.dueño._Corredor__correr = False
        except AttributeError:
            pass
        self.blocking = blocking
        if not self._locked:
            self.accessed = True
            self._locked = True
            return True

        if self._locked:
            return False

    def release(self):
        if self._locked:
            self._locked = False
        return RuntimeError('release unlocked lock')

    def locked(self):
        return self._locked

    def __enter__(self, *args, **kwargs):
        self.acquire()
        return args, kwargs

    def __exit__(self, *args, **kwargs):
        self.release()
        return args, kwargs

class FakeEvent:
    def __init__(self) -> None:
        self._set = False
        self._wait = False
    
    def is_set(self):
        return self._set
    
    def set(self):
        self._set = True
    
    def wait(self):
        self._wait = True

    def __bool__(self):
        return False

class VerificarCarrera(unittest.TestCase):

    @timeout(N_SECOND)
    def setUp(self) -> None:
        tortuga = FakeLock()
        lock_verificar_tortuga = FakeLock()
        senal_inicio = Event()
        senal_fin = Event()

        self.j1 = Corredor('Juan', tortuga, senal_inicio,
                           senal_fin, lock_verificar_tortuga)
        self.j2 = Corredor('Pepe', tortuga, senal_inicio,
                           senal_fin, lock_verificar_tortuga)

        self.j1.asignar_rival(self.j1.ser_notificado_por_robo)

        self.j1._Corredor__velocidad = 10
        Corredor.TIEMPO_ESPERA = 0
        Corredor.PORCENTAJE_MIN = 100
        Corredor.PORCENTAJE_MAX = 100
        Corredor.PROBABILIDAD_ROBAR = 1

        self.carrera = Carrera(self.j1, self.j2, senal_inicio, senal_fin)

    @timeout(N_SECOND)
    def test_carrera_clases_thread(self):
        self.assertIn(Thread, Carrera.__mro__)

    @timeout(N_SECOND)
    def test_carrera_valor_daemon(self):
        self.assertFalse(self.carrera.daemon)

    @timeout(N_SECOND)
    @patch('threading.Thread.join')
    @patch('carrera.Carrera.run')
    def test_empezar_verificar_start(self, *args):
        with patch('threading.Thread.start') as mock:
            self.carrera.empezar()
            mock.assert_called()

    @timeout(N_SECOND)
    @patch('threading.Thread.join')
    @patch('threading.Thread.start')
    def test_empezar_verificar_no_hacer_run(self, *args):
        with patch('carrera.Carrera.run') as mock:
            self.carrera.empezar()
            mock.assert_not_called()

    @timeout(N_SECOND)
    @patch('threading.Thread.start')
    @patch('carrera.Carrera.run')
    def test_empezar_verificar_join(self, *args):
        with patch('threading.Thread.join') as mock:
            self.carrera.empezar()
            mock.assert_called()

    @timeout(N_SECOND)
    @patch('threading.Thread.start')
    @patch('threading.Thread.join')
    @patch('carrera.Carrera.run')
    def test_empezar_verificar_ganadores(self, *args):
        self.j1.tiene_tortuga = True
        self.j2.tiene_tortuga = False
        winner = self.carrera.empezar()
        self.assertEqual(winner, self.j1.name)

        self.j1.tiene_tortuga = False
        self.j2.tiene_tortuga = True
        winner = self.carrera.empezar()
        self.assertEqual(winner, self.j2.name)

    @timeout(N_SECOND)
    def test_run_verificar_start_corredores(self):
        with patch('threading.Thread.start') as mock:
            self.carrera.senal_fin.set()
            self.carrera.run()
            self.assertEqual(mock.call_count, 2)

    @timeout(N_SECOND)
    @patch('threading.Thread.start')
    def test_run_verificar_senal_inicio(self, new_start):
        self.assertFalse(self.carrera.senal_inicio.is_set())
        self.carrera.senal_fin.set()
        self.carrera.run()
        self.assertTrue(self.carrera.senal_inicio.is_set())

    @timeout(N_SECOND)
    @patch('threading.Thread.start')
    def test_run_verificar_senal_fin(self, new_start):
        with patch('threading.Event.wait') as mock:
            self.carrera.run()
            mock.assert_called()


class VerificarCorredor(unittest.TestCase):

    @timeout(N_SECOND)
    def setUp(self) -> None:
        tortuga = FakeLock()
        lock_verificar_tortuga = FakeLock()
        senal_inicio = Event()
        senal_fin = Event()

        # Instancia los corredores y la carrera
        self.j1 = Corredor('Juan', tortuga, senal_inicio,
                           senal_fin, lock_verificar_tortuga)
        self.j2 = Corredor('Pepe', tortuga, senal_inicio,
                           senal_fin, lock_verificar_tortuga)

        lock_verificar_tortuga.dueño = self.j1
        self.j1.asignar_rival(self.j1.ser_notificado_por_robo)

        self.j1._Corredor__velocidad = 10
        Corredor.TIEMPO_ESPERA = 0
        Corredor.PORCENTAJE_MIN = 100
        Corredor.PORCENTAJE_MAX = 100
        Corredor.PROBABILIDAD_ROBAR = 1

    @timeout(N_SECOND)
    def test_corredor_clases_thread(self):
        self.assertIn(Thread, Corredor.__mro__)

    @timeout(N_SECOND)
    def test_corredor_valor_daemon(self):
        self.assertTrue(self.j1.daemon)
        self.assertTrue(self.j2.daemon)

    @timeout(N_SECOND)
    def test_verificar_avanzar(self):
        self.assertEqual(self.j1.posicion, 0)
        self.j1.avanzar()
        self.assertEqual(self.j1.posicion, 10)

    @timeout(N_SECOND)
    def test_intentar_capturar_tortuga_verificar_blocking(self):
        self.assertTrue(self.j1.lock_tortuga.blocking)
        self.j1.intentar_capturar_tortuga()
        self.assertFalse(self.j1.lock_tortuga.blocking)

    @timeout(N_SECOND)
    def test_intentar_capturar_tortuga_verificar_lock(self):
        self.assertFalse(self.j1.tiene_tortuga)
        self.j1.intentar_capturar_tortuga()
        self.assertTrue(self.j1.lock_tortuga.locked())

    @timeout(N_SECOND)
    def test_intentar_capturar_tortuga_resultado_exitoso(self):
        self.assertFalse(self.j1.tiene_tortuga)
        self.j1.intentar_capturar_tortuga()
        self.assertTrue(self.j1.tiene_tortuga)

    @timeout(N_SECOND)
    def test_intentar_capturar_tortuga_resultado_fallido(self):
        self.j1.lock_tortuga.acquire()
        self.assertFalse(self.j1.tiene_tortuga)
        self.j1.intentar_capturar_tortuga()
        self.assertFalse(self.j1.tiene_tortuga)

    @timeout(N_SECOND)
    def test_perder_tortuga_verificar_tortuga(self):
        self.j1.tiene_tortuga = True
        self.j1.perder_tortuga()
        self.assertFalse(self.j1.tiene_tortuga)

    @timeout(N_SECOND)
    def test_perder_tortuga_verificar_lock(self):
        self.j1.lock_tortuga.acquire()
        self.assertTrue(self.j1.lock_tortuga.locked())
        self.j1.perder_tortuga()
        self.assertFalse(self.j1.lock_tortuga.locked())

    @timeout(N_SECOND)
    def test_robar_tortuga_notifica_robo(self):
        with patch('carrera.Corredor.perder_tortuga') as mock:
            self.j1.robar_tortuga()
            mock.assert_called()

    @timeout(N_SECOND)
    def test_robar_tortuga_obtiene_tortuga(self):
        with patch('carrera.Corredor.perder_tortuga'):
            self.assertFalse(self.j1.tiene_tortuga)
            self.j1.robar_tortuga()
            self.assertTrue(self.j1.tiene_tortuga)

    @timeout(N_SECOND)
    def test_robar_tortuga_obtiene_lock(self):
        with patch('carrera.Corredor.perder_tortuga'):
            self.j1.robar_tortuga()
            self.assertTrue(self.j1.lock_tortuga.locked())

    @timeout(N_SECOND)
    def test_robar_tortuga_robo_exitoso(self):
        with patch('carrera.Corredor.perder_tortuga'):
            resultado = self.j1.robar_tortuga()
            self.assertIsInstance(resultado, bool)
            self.assertTrue(resultado)

    @timeout(N_SECOND)
    def test_robar_tortuga_robo_fallido(self):
        with patch('carrera.Corredor.perder_tortuga'):
            self.j1.PROBABILIDAD_ROBAR = 0
            resultado = self.j1.robar_tortuga()
            self.assertIsInstance(resultado, bool)
            self.assertFalse(resultado)

    @timeout(N_SECOND)
    def test_correr_primera_mitad_verificar_llamar_avanzar(self):
        def new_avanzar(*args, **kwargs):
            self.j1.posicion = 100
        self.j1.avanzar = new_avanzar
        self.j1.correr_primera_mitad()
        self.assertEqual(self.j1.posicion, 100)

    @timeout(N_SECOND)
    @patch('carrera.Corredor.intentar_capturar_tortuga')
    def test_correr_segunda_mitad_verificar_avance(self, *args):
        self.llamado = 0

        def new_avanzar(*args, **kwargs):
            self.llamado += 1
            self.j1.posicion = 99

        with patch('carrera.Corredor.avanzar', side_effect=new_avanzar):
            self.j1.senal_fin = FakeEvent()
            self.j1.correr_segunda_mitad()
            self.assertGreaterEqual(self.llamado, 1)
            self.assertEqual(self.j1.posicion, 99)

    @timeout(N_SECOND)
    @patch('carrera.Corredor.avanzar')
    @patch('carrera.Corredor.intentar_capturar_tortuga')
    def test_correr_segunda_mitad_verificar_uso_lock(self, *args):
        self.assertFalse(self.j1.lock_verificar_tortuga.accessed)
        self.j1.correr_segunda_mitad()
        self.assertTrue(self.j1.lock_verificar_tortuga.accessed)

    @timeout(N_SECOND)
    @patch('carrera.Corredor.intentar_capturar_tortuga')
    def test_correr_segunda_mitad_carrera_terminada_avanza_maximo_1_vez(self, *args):
        self.llamado = 0

        def new_avanzar(*args, **kwargs):
            self.llamado += 1

        self.j1.senal_fin.set()
        with patch('carrera.Corredor.avanzar', side_effect=new_avanzar):
            self.j1.correr_segunda_mitad()
            self.assertLessEqual(self.llamado, 1)

    @timeout(N_SECOND)
    @patch('carrera.Corredor.intentar_capturar_tortuga')
    def test_correr_segunda_mitad_carrera_perdida_verficar_retorno_y_uso_de_is_set(self, *args):
        self.j1.senal_fin = FakeEvent()
        self.j1.senal_fin.set()
        resultado = self.j1.correr_segunda_mitad()
        self.assertIsInstance(resultado, bool)
        self.assertFalse(resultado)

    @timeout(N_SECOND)
    @patch('carrera.Corredor.intentar_capturar_tortuga')
    def test_correr_segunda_mitad_carrera_ganada_verficar_retorno(self, *args):
        self.j1.posicion = 100
        self.j1.tiene_tortuga = True
        self.j1.senal_fin = FakeEvent()
        resultado = self.j1.correr_segunda_mitad()
        self.assertIsInstance(resultado, bool)
        self.assertTrue(resultado)

    @timeout(N_SECOND)
    @patch('carrera.Corredor.intentar_capturar_tortuga')
    def test_correr_segunda_mitad_carrera_ganada_verificar_senal(self, *args):
        self.j1.posicion = 100
        self.j1.tiene_tortuga = True
        self.j1.senal_fin = FakeEvent()
        self.j1.correr_segunda_mitad()
        self.assertTrue(self.j1.senal_fin.is_set())

    @timeout(N_SECOND)
    @patch('carrera.Corredor.intentar_capturar_tortuga')
    def test_correr_segunda_mitad_carrera_ganada_verificar_lock(self, *args):
        self.j1.posicion = 100
        self.j1.tiene_tortuga = True
        self.j1.senal_fin = FakeEvent()
        self.j1.lock_tortuga.acquire()
        self.j1.correr_segunda_mitad()
        self.assertFalse(self.j1.lock_tortuga.locked())

    @timeout(N_SECOND)
    @patch('carrera.Corredor.avanzar')
    @patch('carrera.Corredor.intentar_capturar_tortuga')
    def test_correr_segunda_mitad_carrera_verificar_robar_tortuga(self, *args):
        self.called = False

        def robar_tortuga():
            self.called = True
            self.j1._Corredor__correr = False

        with patch('carrera.Corredor.robar_tortuga', side_effect=robar_tortuga):
            self.j1.senal_fin = FakeEvent()
            self.j1.tiene_tortuga = False
            self.j1.correr_segunda_mitad()
            self.assertTrue(self.called)

    @timeout(N_SECOND)
    @patch('carrera.Corredor.correr_primera_mitad')
    @patch('carrera.Corredor.intentar_capturar_tortuga')
    @patch('carrera.Corredor.correr_segunda_mitad')
    def test_run_verificar_senal_inicio(self, *args):
        with patch('threading.Event.wait') as mock:
            self.j1.run()
            mock.assert_called()

    @timeout(N_SECOND)
    @patch('carrera.Corredor.intentar_capturar_tortuga')
    @patch('carrera.Corredor.correr_segunda_mitad')
    def test_run_verificar_correr_primera_mitad(self, *args):
        self.j1._Corredor__correr = False
        self.j1.senal_inicio.set()
        with patch('carrera.Corredor.correr_primera_mitad') as mock:
            self.j1.run()
            mock.assert_called()

    @timeout(N_SECOND)
    @patch('carrera.Corredor.correr_primera_mitad')
    @patch('carrera.Corredor.correr_segunda_mitad')
    def test_run_verificar_intento_captura(self, *args):
        self.j1.senal_inicio.set()
        with patch('carrera.Corredor.intentar_capturar_tortuga') as mock:
            self.j1.run()
            mock.assert_called()

    @timeout(N_SECOND)
    @patch('carrera.Corredor.correr_primera_mitad')
    @patch('carrera.Corredor.intentar_capturar_tortuga')
    def test_run_verificar_correr_segunda_mitad(self, *args):
        self.j1.senal_inicio.set()
        with patch('carrera.Corredor.correr_segunda_mitad') as mock:
            self.j1.run()
            mock.assert_called()


if __name__ == '__main__':
    with patch('sys.stdout', new=StringIO()):
        unittest.main(verbosity=1)

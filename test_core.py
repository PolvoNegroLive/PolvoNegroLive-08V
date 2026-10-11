"""Testes automaticos do nucleo. Rodar:  python -m unittest discover -s tests -v   (ou scripts\\TESTES.bat)"""
import json, os, shutil, socket, subprocess, sys, tempfile, time, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import validation as V, errors as E, ffcmd, performance as P, secrets
from app.settings import Settings
from app import migration

HAS_FF = shutil.which("ffmpeg") is not None


class TestValidation(unittest.TestCase):
    def test_backup_url_do_youtube(self):
        self.assertEqual(V.build_url("rtmp://b.rtmp.youtube.com/live2?backup=1", "AAAA"), "rtmp://b.rtmp.youtube.com/live2/AAAA?backup=1")
        self.assertEqual(V.build_url("rtmps://a.rtmps.youtube.com:443/live2", "AAAA"), "rtmps://a.rtmps.youtube.com:443/live2/AAAA")

    def test_config_do_teste_5_do_usuario(self):
        cap = {"video": "USB Video", "audio": "", "width": 800, "height": 600, "fps": 30}
        a = {"id": "youtube", "name": "YouTube", "enabled": True, "server": "rtmp://saopaulo.restream.io/live", "stream_key": "K1", "width": 720, "height": 800, "fps": 120, "video_bitrate": "25000k"}
        b = dict(a, id="tiktok", name="TikTok", server="rtmp://live.restream.io/live", width=800, height=720, fps=144)
        codes = {i["code"] for i in V.validate_set([a, b], cap)}
        for c in ("FPS_ABOVE_CAPTURE", "BITRATE_ABSURD", "DUP_KEY", "AUDIO_NONE", "ODD_ASPECT"):
            self.assertIn(c, codes)

    def test_config_boa_sem_erros(self):
        cap = {"video": "USB Video", "audio": "Mic", "width": 1280, "height": 720, "fps": 30}
        a = {"id": "yt", "name": "YT", "kind": "youtube", "enabled": True, "server": "rtmps://a.rtmps.youtube.com:443/live2", "stream_key": "K1", "width": 854, "height": 480, "fps": 30, "video_bitrate": "2000k"}
        b = dict(a, id="tt", name="TT", kind="tiktok", server="rtmp://x.tiktok.example/live", stream_key="K2", width=480, height=854)
        self.assertEqual([i for i in V.validate_set([a, b], cap) if i["level"] == "erro"], [])


class TestErrors(unittest.TestCase):
    def test_textos_reais_dos_logs(self):
        self.assertEqual(E.classify("Error opening output file rtmp://live.restream.io/********\nError opening output files: End of file")["code"], "SERVER_CLOSED_CONNECTION")
        self.assertEqual(E.classify("[in#0/mpegts @ 000001fe78152dc0] Error during demuxing: Error number -10054 occurred")["code"], "LOCAL_HUB_RESET")
        self.assertEqual(E.classify("Could not find video device with name [USB Video]")["code"], "CAPTURE_ERROR")
        self.assertEqual(E.classify("Connection to tcp://x:1 failed: Connection refused")["code"], "CONNECTION_REFUSED")


class TestFfcmd(unittest.TestCase):
    def test_entrada_dshow_sem_aspas(self):
        a = ffcmd.input_args({"video": "USB Video", "audio": "Mic", "width": 800, "height": 600, "fps": 30, "format": "mjpeg", "format_opt": "vcodec"})
        self.assertIn("video=USB Video:audio=Mic", a); self.assertNotIn('"', " ".join(a)); self.assertIn("-vcodec", a)

    @unittest.skipUnless(HAS_FF, "sem ffmpeg")
    def test_corte_funciona_em_todas_as_combinacoes(self):
        for src in ("800x600", "1280x720"):
            for w, h in ((854, 480), (480, 854), (720, 720)):
                f = ffcmd.branch_filter({"width": w, "height": h, "fps": 30, "fit": "cortar"})
                r = subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "testsrc=size=%s:rate=30" % src, "-t", "1", "-vf", f, "-f", "null", "-"], capture_output=True)
                self.assertEqual(r.returncode, 0, "%s -> %dx%d" % (src, w, h))

    def test_perfis_identicos_dividem_encode(self):
        d = {"width": 854, "height": 480, "fps": 30, "video_bitrate": "2000k", "fit": "ajustar"}
        self.assertEqual(len(ffcmd.group_profiles([dict(d, id="a"), dict(d, id="b")])), 1)
        self.assertEqual(len(ffcmd.group_profiles([dict(d, id="a"), dict(d, id="b", width=480, height=854)])), 2)


class TestPerformance(unittest.TestCase):
    def test_nunca_passa_do_que_a_camera_entrega(self):
        cap = {"width": 800, "height": 600, "fps": 30}
        for s in range(0, 101, 10):
            p = P.plan(s, cap)
            self.assertLessEqual(p["fps"], 30); self.assertLessEqual(min(p["width"], p["height"]), 600)


class TestSettings(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()

    def test_chave_nao_fica_em_texto_no_arquivo(self):
        s = Settings(self.tmp).load(); s.destinations[0]["stream_key"] = "SEGREDO-123456"; s.save()
        self.assertNotIn("SEGREDO-123456", (s.cfg / "destinations.json").read_text())
        self.assertEqual(Settings(self.tmp).load().destinations[0]["stream_key"], "SEGREDO-123456")

    def test_importa_configuracao_antiga_com_backup(self):
        old = os.path.join(self.tmp, "V06", "config"); os.makedirs(old)
        json.dump({"enabled": True, "server": "rtmp://a/b", "stream_key": "CHAVE-ANTIGA-1", "width": 854, "height": 480, "fps": 30, "video_bitrate": "2000k"}, open(os.path.join(old, "youtube.json"), "w"))
        s = Settings(os.path.join(self.tmp, "dados")); notes = []
        migration.from_legacy(s, notes, legacy_dir=old)
        self.assertEqual(s.destinations[0]["stream_key"], "CHAVE-ANTIGA-1"); self.assertTrue(notes)

    def test_segredos_roundtrip(self):
        self.assertEqual(secrets.unprotect(secrets.protect("abc123"))[0], "abc123")


@unittest.skipUnless(HAS_FF, "sem ffmpeg")
class TestHub(unittest.TestCase):
    def test_destino_entra_no_meio_e_comeca_em_quadro_chave(self):
        from app.hub import Hub
        hub = Hub(1, 20)
        enc = subprocess.Popen(["ffmpeg", "-nostdin", "-loglevel", "error", "-re", "-f", "lavfi", "-i", "testsrc2=size=640x360:rate=30", "-t", "6", "-c:v", "libx264", "-preset", "ultrafast",
                                "-pix_fmt", "yuv420p", "-g", "30", "-keyint_min", "30", "-b:v", "1000k", "-f", "mpegts", "-mpegts_flags", "+resend_headers", "-mpegts_start_pid", "256",
                                "-mpegts_pmt_start_pid", "4096", "tcp://127.0.0.1:%d" % hub.enc_ports[0]])
        time.sleep(2.3)
        s = socket.create_connection(("127.0.0.1", hub.sub_ports[0])); s.settimeout(3); got = b""
        try:
            while len(got) < 400000:
                d = s.recv(65536)
                if not d: break
                got += d
        except socket.timeout:
            pass
        enc.wait(); hub.close()
        self.assertGreater(len(got), 100000)
        p = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-read_intervals", "%+#1", "-show_entries", "packet=flags", "-of", "csv=p=0", "-f", "mpegts", "-"], input=got, capture_output=True)
        self.assertTrue(p.stdout.decode().startswith("K"))


if __name__ == "__main__":
    unittest.main(verbosity=2)

from emu68hatcher.builder.staging.scripts.injector import (
    apply_standard_injections,
    read_amiga_script,
)
from emu68hatcher.data.package_loader import get_local_packages_dir

# Cloanto Amiga Forever 3.1 Startup-Sequence: SetPatch nested in If blocks,
# monitors loaded inline instead of via LoadMonDrvs
AMIGA_FOREVER_STARTUP = """\
; $VER: Startup-Sequence_HardDrive 40.5 (30.12.99)
; Startup-Sequence for hard drive systems

FailAt 21
C:Version >NIL: exec.library 45 20
If WARN
  C:SetPatch QUIET
Else
  C:SetPatch NOROMUPDATE QUIET
EndIf

BindDrivers
C:Mount >NIL: DEVS:DOSDrivers/~(#?.info)

IF EXISTS DEVS:Monitors
  C:List >NIL: DEVS:Monitors/~(#?.info|VGAOnly) TO T:M LFORMAT "DEVS:Monitors/%s"
  Execute T:M
EndIF

C:IPrefs
C:LoadWB
EndCLI >NIL:
"""


def test_amiga_forever_startup_sequence_is_injected(tmp_path):
    startup = tmp_path / "S" / "Startup-Sequence"
    startup.parent.mkdir()
    startup.write_text(AMIGA_FOREVER_STARTUP, encoding="iso-8859-1")

    results = apply_standard_injections(tmp_path, get_local_packages_dir() / "System")

    assert [r.error for r in results if r.error] == []
    lines = read_amiga_script(startup)
    iconlib = lines.index(";Iconlib - Added by Emu68 Hatcher - BEGIN")
    assert iconlib < lines.index("FailAt 21")
    mount = lines.index("Mount >NIL: DEVS:DOSDrivers/~(#?.info)")
    assert lines.index(";UAEGFX Monitor Swap - Added by Emu68 Hatcher - END") < mount
    assert mount < lines.index("IF EXISTS DEVS:Monitors")
    assert "C:Mount >NIL: DEVS:DOSDrivers/~(#?.info)" not in lines

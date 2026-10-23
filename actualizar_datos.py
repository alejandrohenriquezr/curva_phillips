"""Descarga y valida las cuatro fuentes antes de sustituir el corte local."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import tempfile

ROOT = Path(__file__).resolve().parent
SOURCES = ('ine_ipc_chile.csv', 'ine_ene_chile.csv', 'ine_ir_chile.csv',
           'bcch_imacec_chile.csv', 'fuentes/imacec_metadata.json')


def actualizar(root=ROOT):
    from main import main as descargar_ine
    from actualizar_imacec import main as descargar_bcch
    from phillips import load_data

    root = Path(root)
    # Todo se prepara en el mismo sistema de archivos. Una descarga o validación
    # fallida conserva intactos todos los insumos anteriores.
    with tempfile.TemporaryDirectory(prefix='.actualizacion-', dir=root) as folder:
        stage = Path(folder)
        (stage / 'fuentes').mkdir()
        descargar_ine(stage)
        descargar_bcch(stage)
        data, coverage, _ = load_data(stage)
        csvs = [root / name for name in SOURCES if name.endswith('.csv')]
        if all(path.exists() for path in csvs):
            before, old_coverage, _ = load_data(root)
            if data.fecha.min() > before.fecha.min() or data.fecha.max() < before.fecha.max():
                raise ValueError('La descarga reduce el período común; se conserva el corte anterior')
            for row in coverage.itertuples(index=False):
                old = old_coverage.set_index('serie').loc[row.serie]
                if row.desde > old.desde or row.hasta < old.hasta or row.filas < old.filas:
                    raise ValueError(f'La descarga pierde cobertura en {row.serie}')
        manifest = {
            'descargado_utc': datetime.now(timezone.utc).isoformat(),
            'periodo_comun': {'desde': data.mes.iloc[0], 'hasta': data.mes.iloc[-1], 'n': len(data)},
            'cobertura': coverage.to_dict('records'),
            'sha256': {name: hashlib.sha256((stage/name).read_bytes()).hexdigest() for name in SOURCES},
        }
        (stage/'fuentes/actualizacion.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
        names = (*SOURCES, 'fuentes/actualizacion.json')
        backups = {}
        replaced = []
        try:
            for name in names:
                dest = root/name
                dest.parent.mkdir(exist_ok=True)
                if dest.exists():
                    backup = stage/'backup'/name
                    backup.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(dest, backup)
                    backups[name] = backup
                (stage/name).replace(dest)
                replaced.append(name)
        except Exception:
            for name in reversed(replaced):
                if name in backups:
                    backups[name].replace(root/name)
                else:
                    (root/name).unlink(missing_ok=True)
            raise
    print(coverage.to_string(index=False))
    print(f'Fuentes oficiales actualizadas: período común {data.mes.iloc[0]} a {data.mes.iloc[-1]} ({len(data)} meses)')
    return manifest


if __name__ == '__main__':
    actualizar()

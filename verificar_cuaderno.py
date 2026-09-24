from salidas import archivo, FECHA
from pathlib import Path
import sys
import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager

root=Path(__file__).resolve().parent
nb=nbformat.read(root/archivo('Curva_de_Phillips.ipynb'),as_version=4)
nbformat.validate(nb)
# Fuerza el kernel al mismo intérprete que ejecuta el orquestador.
manager=KernelManager(kernel_name='python3')
manager.kernel_spec.argv=[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}']
print('Python ejecutor y kernel:',sys.executable,flush=True)
client=NotebookClient(nb,timeout=600,km=manager,resources={'metadata':{'path':str(root)}})
client.execute()
nbformat.write(nb,root/archivo('Curva_de_Phillips.ipynb'))
from nbformat.sign import NotebookNotary
NotebookNotary().sign(nb)
errors=[o for c in nb.cells if c.cell_type=='code' for o in c.get('outputs',[]) if o.output_type=='error']
assert not errors
print('Cuaderno ejecutado sin errores. Celdas de código:',sum(c.cell_type=='code' for c in nb.cells),flush=True)


from pathlib import Path
import sys
import nbformat
from nbclient import NotebookClient
from jupyter_client.kernelspec import KernelSpecManager

root=Path(__file__).resolve().parent
nb=nbformat.read(root/'Curva_de_Phillips.ipynb',as_version=4)
nbformat.validate(nb)
# El kernel python3 de este entorno usa sys.executable; confirmar antes de ejecutar.
km=KernelSpecManager()
spec=km.get_kernel_spec('python3')
print('Python ejecutor:',sys.executable,flush=True)
print('Kernel:',spec.argv,flush=True)
client=NotebookClient(nb,timeout=300,kernel_name='python3',resources={'metadata':{'path':str(root)}})
client.execute()
nbformat.write(nb,root/'Curva_de_Phillips.ipynb')
from nbformat.sign import NotebookNotary
NotebookNotary().sign(nb)
errors=[o for c in nb.cells if c.cell_type=='code' for o in c.get('outputs',[]) if o.output_type=='error']
assert not errors
print('Cuaderno ejecutado sin errores. Celdas de código:',sum(c.cell_type=='code' for c in nb.cells),flush=True)


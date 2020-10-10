# PeakFinder 1.0.0Alpha02

Escribir descripción de la app.


## Caracteristicas pendientes
Estas son caracteristicas y funciones pendientes a realizar en futuras compilaciones de la app.

#### Frontend

#### Backend
1. El proceso de cargar datos y calcular se debe hacer por un thread, cuando se retorne un dato se debe ocultar el preloader
2. Si el usuario no existe firebase retorna un error 400 si es así eliminar private.json de lo contrario la app no se ejecuta

## Solución de problemas

Los problemas más comunes con esta librería suelen ser **hidden imports** los cuales pueden ser reparados fácilmente desde **src/build/settings/< nombre del archivo.json >** simplemente agregando una lista con la llave "**hidden imports**" y colocando los paquetes que se desean utilizar.

``` JSON
    {
	    "app_name": "Paquete",
	    "author": "Null",
	    "main_module": "src/main/python/main.py",
	    "version": "1,0,0",
	    "hidden_imports": []
    }
```
En esta app las librerías que más problemas generan se pueden resolver haciendo click en la librería que te de problemas.


## gcloud
Este es el más fácil de resolver, solo tienes que seguir las siguientes instrucciones.

 1. Acceder a tu entorno de desarrollo y entrar a `Lib\site-packages\PyInstaller\hooks`.
 2. Crear un archivo llamado 'hook-gcloud.py'.
 3. Escribir el siguiente código en el archivo:
    ``` python
    from PyInstaller.utils.hooks import copy_metadata
    datas = copy_metadata('gcloud')
    ```
   
## pyrebase
Para resolver este solamente debes añadirlo a **hiden_imports** en **src/build/settings/**.

``` JSON
    {
	    "app_name": "Paquete",
	    "author": "Null",
	    "main_module": "src/main/python/main.py",
	    "version": "1,0,0",
	    "hidden_imports": ["pyrebase", ...]
	}
```
## scipy

Tienes que ir a los hooks de pyinstaller y buscar hook-scipy.py (o crearlo) y pegar esto:

    from PyInstaller.utils.hooks import collect_submodules
	from PyInstaller.utils.hooks import collect_data_files
	hiddenimports = collect_submodules('scipy')
	datas = collect_data_files('scipy') 

Después buscar el archivo hook-sklearn.metrics.cluster.py y modificarlo, debe verse así:
``` python
from PyInstaller.utils.hooks import collect_data_files

hiddenimports = ['sklearn.utils.sparsetools._graph_validation',
                 'sklearn.utils.sparsetools._graph_tools',
                 'sklearn.utils.lgamma',
                 'sklearn.utils.weight_vector']

datas = collect_data_files('sklearn')
```
Esto es opcional pero se recomienda crear el archivo hook-sklearn.py y pegar lo siguiente:
```python
from PyInstaller.utils.hooks import collect_submodules
hiddenimports = collect_submodules('sklearn')
```

## statsmodels
Este es el más complicado ya que si actualizas el hook debes actualizar el archivo que estés utilizando en settings así que comenzaremos por el hook.

#### Hook

 1. Debes crear hook-statsmodels.py' en los hooks de pyinstaller
 2. Escribir el siguiente codigo dentro del archivo:
``` python
hiddenimports=[
    'statsmodels.tsa.statespace._kalman_filter',
    'statsmodels.tsa.statespace._kalman_smoother',
    'statsmodels.tsa.statespace._representation',
    'statsmodels.tsa.statespace._simulation_smoother',
    'statsmodels.tsa.statespace._statespace',
    'statsmodels.tsa.statespace._tools',
    'statsmodels.tsa.statespace._filters._conventional',
    'statsmodels.tsa.statespace._filters._inversions',
    'statsmodels.tsa.statespace._filters._univariate',
    'statsmodels.tsa.statespace._filters._univariate_diffuse',
    'statsmodels.tsa.statespace._smoothers._univariate_diffuse', 
    'statsmodels.tsa.statespace._smoothers._alternative',
    'statsmodels.tsa.statespace._smoothers._classical',
    'statsmodels.tsa.statespace._smoothers._conventional',
    'statsmodels.tsa.statespace._smoothers._univariate'
]
```
#### hidden_imports
 
 1. Pegar lo siguiente en **hidden_imports**:
``` python
"hidden_imports": [
    'statsmodels.tsa.statespace._kalman_filter',
    'statsmodels.tsa.statespace._kalman_smoother',
    'statsmodels.tsa.statespace._representation',
    'statsmodels.tsa.statespace._simulation_smoother',
    'statsmodels.tsa.statespace._statespace',
    'statsmodels.tsa.statespace._tools',
    'statsmodels.tsa.statespace._filters._conventional',
    'statsmodels.tsa.statespace._filters._inversions',
    'statsmodels.tsa.statespace._filters._univariate',
    'statsmodels.tsa.statespace._filters._univariate_diffuse',
    'statsmodels.tsa.statespace._smoothers._univariate_diffuse', 
    'statsmodels.tsa.statespace._smoothers._alternative',
    'statsmodels.tsa.statespace._smoothers._classical',
    'statsmodels.tsa.statespace._smoothers._conventional',
    'statsmodels.tsa.statespace._smoothers._univariate'
]
```

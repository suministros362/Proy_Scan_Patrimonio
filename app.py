from controllers.patrimonio_controller import PatrimonioController
from ui.main_window import MainWindow

def main():
    # 1. Crear el controlador (este instancia sus servicios, repositorios, etc.)
    controller = PatrimonioController()

    # 2. Pasar el controlador a la UI
    app = MainWindow(controller)
    
    # 3. Arrancar la app
    app.mainloop()

if __name__ == "__main__":
    main()
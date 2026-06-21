-- Base de datos
CREATE DATABASE ferreteria_simkin;
USE ferreteria_simkin;



-- Tabla de productos
CREATE TABLE Productos (
    id_producto INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    categoria VARCHAR(50),
    stock_actual INT DEFAULT 0,
    costo_unitario DECIMAL(10,2) NOT NULL,
    proveedor VARCHAR(100),
    clasificacion_ABC CHAR(1) 
);

-- Tabla de movimientos de inventario
CREATE TABLE Movimientos (
    id_movimiento INT AUTO_INCREMENT PRIMARY KEY,
    id_producto INT NOT NULL,
    tipo ENUM('entrada','salida') NOT NULL,
    cantidad INT NOT NULL,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    costo_total DECIMAL(12,2),
    FOREIGN KEY (id_producto) REFERENCES Productos(id_producto)
);

-- Tabla de parámetros para modelos cuantitativos
CREATE TABLE Parametros (
    id_parametro INT AUTO_INCREMENT PRIMARY KEY,
    id_producto INT NOT NULL,
    demanda_anual INT,
    costo_pedido DECIMAL(10,2),
    costo_mantenimiento DECIMAL(10,2), -- Ch por unidad/año
    tiempo_entrega INT, -- en días
    variabilidad_demanda DECIMAL(10,2), -- σd
    FOREIGN KEY (id_producto) REFERENCES Productos(id_producto)
);



-- Tabla de resultados de modelos (opcional, para trazabilidad)
CREATE TABLE Resultados_Modelos (
    id_resultado INT AUTO_INCREMENT PRIMARY KEY,
    id_producto INT NOT NULL,
    EOQ INT,
    PRO INT,
    inventario_seguridad INT,
    fecha_calculo DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_producto) REFERENCES Productos(id_producto)
);



ALTER TABLE Productos
DROP COLUMN clasificacion_ABC;

ALTER TABLE Resultados_Modelos
ADD COLUMN ventas_anuales DECIMAL(12,2),
ADD COLUMN porcentaje DECIMAL(5,2),
ADD COLUMN porcentaje_acumulado DECIMAL(5,2),
ADD COLUMN costo_anual_ordenar DECIMAL(12,2),
ADD COLUMN costo_anual_conservacion DECIMAL(12,2),
ADD COLUMN costo_total DECIMAL(12,2),
ADD COLUMN punto_reorden INT,
ADD COLUMN clasificacion_ABC CHAR(1);



select * from Productos;
select * from Resultados_Modelos;

drop table Resultados_Modelos;

select * from Parametros;
select * from Movimientos;

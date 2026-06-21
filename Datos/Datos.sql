USE ferreteria_simkin;


drop table Parametros;
USE ferreteria_simkin;

-- Limpiar parámetros anteriores
DELETE FROM Parametros;

-- Reiniciar AUTO_INCREMENT opcional
ALTER TABLE Parametros AUTO_INCREMENT = 1;

INSERT INTO Parametros (
    id_producto,
    demanda_anual,
    costo_pedido,
    costo_mantenimiento,
    tiempo_entrega,
    variabilidad_demanda
)
SELECT
    p.id_producto,
    /* =========================
       DEMANDA ANUAL
       ========================= */

    CASE
        /* Productos caros y críticos */
        WHEN p.costo_unitario >= 100000 THEN
            ROUND(50 + (RAND() * 250), 0)

        /* Productos valor medio */
        WHEN p.costo_unitario >= 20000 THEN
            ROUND(200 + (RAND() * 800), 0)
        /* Productos baratos / alta rotación */
        ELSE
            ROUND(800 + (RAND() * 3500), 0)
    END AS demanda_anual,
    /* =========================
       COSTO DE PEDIDO (Co)
       ========================= */
    CASE
        /* Equipos pesados o importados */
        WHEN p.costo_unitario >= 100000 THEN
            ROUND(15000 + (RAND() * 20000), 2)

        /* Productos intermedios */
        WHEN p.costo_unitario >= 20000 THEN
            ROUND(8000 + (RAND() * 12000), 2)

        /* Productos comunes */
        ELSE
            ROUND(3000 + (RAND() * 7000), 2)

    END AS costo_pedido,
    /* =========================
       COSTO DE MANTENIMIENTO (Ch)
       Basado en porcentaje anual
       ========================= */

    ROUND(
        p.costo_unitario *
        (
            CASE

                /* Productos caros tienen mayor costo de conservación */
                WHEN p.costo_unitario >= 100000 THEN
                    0.25 + (RAND() * 0.10)

                /* Intermedios */
                WHEN p.costo_unitario >= 20000 THEN
                    0.18 + (RAND() * 0.08)

                /* Económicos */
                ELSE
                    0.10 + (RAND() * 0.10)

            END
        ),
    2) AS costo_mantenimiento,
    /* =========================
       TIEMPO DE ENTREGA
       ========================= */
    CASE

        /* Importados o complejos */
        WHEN p.costo_unitario >= 100000 THEN
            FLOOR(10 + (RAND() * 15))

        /* Intermedios */
        WHEN p.costo_unitario >= 20000 THEN
            FLOOR(5 + (RAND() * 8))

        /* Productos comunes */
        ELSE
            FLOOR(2 + (RAND() * 5))

    END AS tiempo_entrega,


    /* =========================
       VARIABILIDAD DEMANDA (σd)
       Aproximadamente 5%-20%
	========================= */
    ROUND(
        (
            CASE
                WHEN p.costo_unitario >= 100000 THEN
                    (50 + (RAND() * 250)) * (0.05 + RAND()*0.10)
                WHEN p.costo_unitario >= 20000 THEN
                    (200 + (RAND() * 800)) * (0.08 + RAND()*0.12)
                ELSE
                    (800 + (RAND() * 3500)) * (0.10 + RAND()*0.15)
            END
        ),
    2) AS variabilidad_demanda
FROM Productos p;

-- Recalcular variabilidad de la demanda con un rango fijo
-- y limitarla a un máximo de 100 unidades

UPDATE Parametros
SET variabilidad_demanda = LEAST(
    ROUND(4 + (RAND() * 60), 2), 100
);


CREATE TRIGGER recalcular_variabilidad
BEFORE INSERT ON Parametros
FOR EACH ROW
SET NEW.variabilidad_demanda = LEAST(ROUND(4 + (RAND() * 60), 2), 100);

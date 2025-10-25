
CREATE OR ALTER PROCEDURE SP_REGISTRAR_VENTA
AS
BEGIN
	SET NOCOUNT ON;

	DECLARE
        @IDVENTA INT,
        @NUM_INSERTS INT,
    	@I INT,
        @IDCELULAR INT,
        @PRECIO REAL,
        @SUBTOTAL REAL,
    	@IVA REAL,
    	@TOTAL REAL,
        @IDDETALLE INT;

	DECLARE CUR_VENTAS CURSOR FOR
    	SELECT V.IDVENTA
    	FROM VENTA V
    	WHERE YEAR(V.FECHA_REGISTRO) = YEAR(GETDATE())
      	AND NOT EXISTS (
              SELECT 1 FROM VENTADETALLE VD WHERE VD.IDVENTA = V.IDVENTA
      	);

	OPEN CUR_VENTAS;
	FETCH NEXT FROM CUR_VENTAS INTO @IDVENTA;

	WHILE @@FETCH_STATUS = 0
	BEGIN
    	BEGIN TRY
            BEGIN TRANSACTION;

        	-- Número aleatorio de detalles (1–5)
        	SET @NUM_INSERTS = (ABS(CHECKSUM(NEWID())) % 5) + 1;
            SET @I = 1;
            SET @SUBTOTAL = 0;

            WHILE @I <= @NUM_INSERTS
            BEGIN
            	-- Generar manualmente el ID del detalle
            	SELECT @IDDETALLE = ISNULL(MAX(IDVENTADETALLE), 0) + 1 FROM VENTADETALLE;

            	-- Seleccionar celular aleatorio válido
            	SELECT TOP 1
                	@IDCELULAR = C.IDCELULAR,
                	@PRECIO = C.PRECIO
                FROM CELULAR C
                WHERE C.PRECIO BETWEEN 100 AND 300
                  	AND LEFT(C.IMEI,1) NOT LIKE '[0-9]'
                  	AND C.STOCK > 0
                ORDER BY NEWID();

                IF @IDCELULAR IS NOT NULL
                BEGIN
                	INSERT INTO VENTADETALLE (IDVENTADETALLE, IDVENTA, IDCELULAR, CANT, PRECIO, SUBTOTAL)
                	VALUES (@IDDETALLE, @IDVENTA, @IDCELULAR, 1, @PRECIO, @PRECIO);

                	SET @SUBTOTAL += @PRECIO;
                	UPDATE CELULAR SET STOCK = STOCK - 1 WHERE IDCELULAR = @IDCELULAR;
                END

                SET @I += 1;
            END

            -- Calcular totales (IVA 12%)
            SET @IVA = @SUBTOTAL * 0.12;
            SET @TOTAL = @SUBTOTAL + @IVA;

            UPDATE VENTA
            SET SUBTOTAL = @SUBTOTAL,
                IVA = @IVA,
                DSCTO = 0.00,
                TOTAL = @TOTAL
            WHERE IDVENTA = @IDVENTA;

            COMMIT TRANSACTION;
        	PRINT 'VENTA PROCESADA CORRECTAMENTE: ' + CAST(@IDVENTA AS VARCHAR(10));
    	END TRY
    	BEGIN CATCH
            ROLLBACK TRANSACTION;
            PRINT 'ERROR EN LA VENTA ' + CAST(@IDVENTA AS VARCHAR(10)) + ': ' + ERROR_MESSAGE();
    	END CATCH;

    	FETCH NEXT FROM CUR_VENTAS INTO @IDVENTA;
	END

	CLOSE CUR_VENTAS;
	DEALLOCATE CUR_VENTAS;
END;
GO




-- ######################    PROBAR CURSOR  ##################################
--Cliente existe y fecha también
EXEC SP_REGISTRAR_VENTA;
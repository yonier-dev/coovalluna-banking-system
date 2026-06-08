-- =====================
-- AGENCIAS (3)
-- =====================
INSERT INTO AGENCIA VALUES ('AG01', '3222100001', 'Tuluá', 'Tuluá Centro', '1991-03-15 08:00:00', 'Calle 25 #10-30');
INSERT INTO AGENCIA VALUES ('AG02', '3222100002', 'Riofrío', 'Riofrío', '1995-06-01 08:00:00', 'Carrera 5 #8-12');
INSERT INTO AGENCIA VALUES ('AG03', '3222100003', 'Trujillo', 'Trujillo', '1998-09-20 08:00:00', 'Calle 10 #4-50');

-- =====================
-- CARGOS
-- =====================
INSERT INTO CARGO (cod_cargo_pk, Nombre, turno, ventanilla_asignada) VALUES ('C01', 'Director Regional', 'Diurno', NULL);
INSERT INTO CARGO (cod_cargo_pk, Nombre, turno, ventanilla_asignada) VALUES ('C02', 'Director Agencia', 'Diurno', NULL);
INSERT INTO CARGO (cod_cargo_pk, Nombre, turno, ventanilla_asignada) VALUES ('C03', 'Asesor Comercial', 'Diurno', 'V1');
INSERT INTO CARGO (cod_cargo_pk, Nombre, turno, ventanilla_asignada) VALUES ('C04', 'Cajero', 'Diurno', 'V2');

-- =====================
-- EMPLEADOS (6) con jerarquía
-- =====================
-- Director Regional (supervisa directores de agencia)
INSERT INTO EMPLEADO (Cedula_pk, CodigoAgencia_fk, Tipo_labor, Correo_corp, Nombres, Apellidos, cod_cargo_fk, Fecha_Ingreso, Salario_base, Estado_Laboral, password)
VALUES ('1000001', 'AG01', 'admin', 'hernando.munoz@coovalluna.com', 'Hernando', 'Muñoz', 'C01', '1991-03-15 08:00:00', 5000000, 'activo', '1234');

-- Director Agencia Tuluá
INSERT INTO EMPLEADO (Cedula_pk, CodigoAgencia_fk, Tipo_labor, Correo_corp, Nombres, Apellidos, cod_cargo_fk, Fecha_Ingreso, Salario_base, Estado_Laboral, password)
VALUES ('1000002', 'AG01', 'admin', 'gustavo.erazo@coovalluna.com', 'Gustavo', 'Erazo', 'C02', '1995-01-10 08:00:00', 3500000, 'activo', '1234');

-- Director Agencia Trujillo
INSERT INTO EMPLEADO (Cedula_pk, CodigoAgencia_fk, Tipo_labor, Correo_corp, Nombres, Apellidos, cod_cargo_fk, Fecha_Ingreso, Salario_base, Estado_Laboral, password)
VALUES ('1000003', 'AG03', 'admin', 'andrea.castano@coovalluna.com', 'Andrea', 'Castaño', 'C02', '2000-05-20 08:00:00', 3500000, 'activo', '1234');

-- Asesores
INSERT INTO EMPLEADO (Cedula_pk, CodigoAgencia_fk, Tipo_labor, Correo_corp, Nombres, Apellidos, cod_cargo_fk, Fecha_Ingreso, Salario_base, Estado_Laboral, password)
VALUES ('1000004', 'AG01', 'asesor', 'carlos.lopez@coovalluna.com', 'Carlos', 'López', 'C03', '2010-03-01 08:00:00', 2000000, 'activo', '1234');

INSERT INTO EMPLEADO (Cedula_pk, CodigoAgencia_fk, Tipo_labor, Correo_corp, Nombres, Apellidos, cod_cargo_fk, Fecha_Ingreso, Salario_base, Estado_Laboral, password)
VALUES ('1000005', 'AG02', 'asesor', 'maria.garcia@coovalluna.com', 'María', 'García', 'C03', '2015-07-15 08:00:00', 2000000, 'activo', '1234');

INSERT INTO EMPLEADO (Cedula_pk, CodigoAgencia_fk, Tipo_labor, Correo_corp, Nombres, Apellidos, cod_cargo_fk, Fecha_Ingreso, Salario_base, Estado_Laboral, password)
VALUES ('1000006', 'AG03', 'asesor', 'luis.torres@coovalluna.com', 'Luis', 'Torres', 'C04', '2018-11-01 08:00:00', 1800000, 'activo', '1234');

-- =====================
-- JERARQUIA SUPERVISA
-- =====================
-- Hernando supervisa a Gustavo y Andrea (directores)
INSERT INTO SUPERVISA VALUES ('1000001', '1000002');
INSERT INTO SUPERVISA VALUES ('1000001', '1000003');
-- Gustavo supervisa asesores de Tuluá
INSERT INTO SUPERVISA VALUES ('1000002', '1000004');
-- Andrea supervisa asesores de Trujillo
INSERT INTO SUPERVISA VALUES ('1000003', '1000006');
-- María reporta a Gustavo también
INSERT INTO SUPERVISA VALUES ('1000002', '1000005');

-- =====================
-- ASOCIADOS (10)
-- 3 fundadores + 7 activos
-- =====================
INSERT INTO ASOCIADO VALUES ('2000001', 'Emilce', 'Rentería', '1955-04-10', '3101234001', 'activo', '1991-03-15 08:00:00', 'Tuluá', 'emilce@gmail.com', 'Calle 12 #3-10', '1234', 0, FALSE);
INSERT INTO ASOCIADO VALUES ('2000002', 'Jorge', 'Salcedo', '1960-08-22', '3101234002', 'activo', '1991-03-15 08:00:00', 'Tuluá', 'jorge@gmail.com', 'Carrera 8 #5-20', '1234', 0, FALSE);
INSERT INTO ASOCIADO VALUES ('2000003', 'Rosa', 'Montoya', '1958-11-05', '3101234003', 'activo', '1993-06-01 08:00:00', 'Riofrío', 'rosa@gmail.com', 'Calle 6 #2-15', '1234', 0, FALSE);
INSERT INTO ASOCIADO VALUES ('2000004', 'Pedro', 'Cardona', '1975-02-14', '3101234004', 'activo', '2005-01-20 08:00:00', 'Tuluá', 'pedro@gmail.com', 'Calle 18 #7-30', '1234', 0, FALSE);
INSERT INTO ASOCIADO VALUES ('2000005', 'Laura', 'Ospina', '1988-07-30', '3101234005', 'activo', '2010-03-10 08:00:00', 'Trujillo', 'laura@gmail.com', 'Carrera 3 #9-40', '1234', 0, FALSE);
INSERT INTO ASOCIADO VALUES ('2000006', 'Andrés', 'Vargas', '1990-12-01', '3101234006', 'activo', '2012-08-05 08:00:00', 'Tuluá', 'andres@gmail.com', 'Calle 22 #11-50', '1234', 0, FALSE);
INSERT INTO ASOCIADO VALUES ('2000007', 'Claudia', 'Ríos', '1982-05-18', '3101234007', 'suspendido', '2008-04-15 08:00:00', 'Riofrío', 'claudia@gmail.com', 'Carrera 6 #4-25', '1234', 0, FALSE);
INSERT INTO ASOCIADO VALUES ('2000008', 'Fernando', 'Castro', '1979-09-25', '3101234008', 'activo', '2015-11-30 08:00:00', 'Trujillo', 'fernando@gmail.com', 'Calle 9 #1-60', '1234', 0, FALSE);
INSERT INTO ASOCIADO VALUES ('2000009', 'Natalia', 'Herrera', '1995-03-08', '3101234009', 'activo', '2020-02-14 08:00:00', 'Tuluá', 'natalia@gmail.com', 'Carrera 10 #6-35', '1234', 0, FALSE);
INSERT INTO ASOCIADO VALUES ('2000010', 'Camilo', 'Parra', '1985-06-12', '3101234010', 'retirado', '2007-07-20 08:00:00', 'Andalucía', 'camilo@gmail.com', 'Calle 15 #8-45', '1234', 0, FALSE);

-- =====================
-- FUNDADORES (3)
-- =====================
INSERT INTO ASOCIADO_FUND VALUES ('2000001', 'ACTA-001', 1991, 'Exención parcial cuota sostenimiento, acceso preferencial créditos bajo interés, voz y voto asamblea extraordinaria', '1991-03-15 08:00:00');
INSERT INTO ASOCIADO_FUND VALUES ('2000002', 'ACTA-001', 1991, 'Exención parcial cuota sostenimiento, acceso preferencial créditos bajo interés, voz y voto asamblea extraordinaria', '1991-03-15 08:00:00');
INSERT INTO ASOCIADO_FUND VALUES ('2000003', 'ACTA-002', 1993, 'Exención parcial cuota sostenimiento, acceso preferencial créditos bajo interés, voz y voto asamblea extraordinaria', '1993-06-01 08:00:00');

-- =====================
-- BENEFICIARIOS (4)
-- =====================
INSERT INTO BENEFICIARIO VALUES ('3000001', '2000001', 'hijo/a', 'Manuel Rentería López', 60.0, '3201111001');
INSERT INTO BENEFICIARIO VALUES ('3000002', '2000001', 'cónyuge', 'Gloria López de Rentería', 40.0, '3201111002');
INSERT INTO BENEFICIARIO VALUES ('3000003', '2000004', 'hijo/a', 'Sara Cardona Díaz', 50.0, '3201111003');
INSERT INTO BENEFICIARIO VALUES ('3000004', '2000004', 'hijo/a', 'Juan Cardona Díaz', 50.0, '3201111004');

-- =====================
-- CUENTAS DE AHORRO (5)
-- =====================
INSERT INTO CUENTA_AHORRO VALUES ('CTA-001', 'AG01', '2000001', '2010-01-15 08:00:00', 'activa');
INSERT INTO CUENTA_AHORRO VALUES ('CTA-002', 'AG01', '2000004', '2015-03-20 08:00:00', 'activa');
INSERT INTO CUENTA_AHORRO VALUES ('CTA-003', 'AG02', '2000005', '2018-07-10 08:00:00', 'activa');
INSERT INTO CUENTA_AHORRO VALUES ('CTA-004', 'AG03', '2000006', '2020-11-05 08:00:00', 'activa');
INSERT INTO CUENTA_AHORRO VALUES ('CTA-005', 'AG01', '2000009', '2022-04-18 08:00:00', 'inactiva');

-- =====================
-- MOVIMIENTOS (15)
-- =====================
INSERT INTO MOVIMIENTO (num_transaccion_pk, Saldo, Tipo_Movimiento, Canal, Valor, Fecha_Hora, cuenta_a_la_que_pertenece) VALUES ('TRX-001', 500000, 'deposito', 'presencial', 500000, '2024-01-10 09:00:00+00', 'CTA-001');
INSERT INTO MOVIMIENTO (num_transaccion_pk, Saldo, Tipo_Movimiento, Canal, Valor, Fecha_Hora, cuenta_a_la_que_pertenece) VALUES ('TRX-002', 800000, 'deposito', 'aplicación móvil', 300000, '2024-02-05 10:30:00+00', 'CTA-001');
INSERT INTO MOVIMIENTO (num_transaccion_pk, Saldo, Tipo_Movimiento, Canal, Valor, Fecha_Hora, cuenta_a_la_que_pertenece) VALUES ('TRX-003', 600000, 'retiro', 'cajero automático', 200000, '2024-03-12 14:00:00+00', 'CTA-001');
INSERT INTO MOVIMIENTO (num_transaccion_pk, Saldo, Tipo_Movimiento, Canal, Valor, Fecha_Hora, cuenta_a_la_que_pertenece, cuenta_destino) VALUES ('TRX-004', 400000, 'transferencia saliente', 'aplicación móvil', 200000, '2024-04-01 11:00:00+00', 'CTA-001', 'CTA-002');
INSERT INTO MOVIMIENTO (num_transaccion_pk, Saldo, Tipo_Movimiento, Canal, Valor, Fecha_Hora, cuenta_a_la_que_pertenece, cuenta_origen) VALUES ('TRX-005', 200000, 'transferencia entrante', 'aplicación móvil', 200000, '2024-04-01 11:01:00+00', 'CTA-002', 'CTA-001');
INSERT INTO MOVIMIENTO (num_transaccion_pk, Saldo, Tipo_Movimiento, Canal, Valor, Fecha_Hora, cuenta_a_la_que_pertenece) VALUES ('TRX-006', 1000000, 'deposito', 'presencial', 800000, '2024-01-20 09:00:00+00', 'CTA-002');
INSERT INTO MOVIMIENTO (num_transaccion_pk, Saldo, Tipo_Movimiento, Canal, Valor, Fecha_Hora, cuenta_a_la_que_pertenece) VALUES ('TRX-007', 700000, 'retiro', 'cajero automático', 300000, '2024-02-28 15:00:00+00', 'CTA-002');
INSERT INTO MOVIMIENTO (num_transaccion_pk, Saldo, Tipo_Movimiento, Canal, Valor, Fecha_Hora, cuenta_a_la_que_pertenece) VALUES ('TRX-008', 1500000, 'deposito', 'presencial', 800000, '2024-03-05 08:30:00+00', 'CTA-003');
INSERT INTO MOVIMIENTO (num_transaccion_pk, Saldo, Tipo_Movimiento, Canal, Valor, Fecha_Hora, cuenta_a_la_que_pertenece) VALUES ('TRX-009', 1200000, 'retiro', 'presencial', 300000, '2024-04-10 10:00:00+00', 'CTA-003');
INSERT INTO MOVIMIENTO (num_transaccion_pk, Saldo, Tipo_Movimiento, Canal, Valor, Fecha_Hora, cuenta_a_la_que_pertenece) VALUES ('TRX-010', 2000000, 'deposito', 'aplicación móvil', 800000, '2024-05-15 09:00:00+00', 'CTA-003');
INSERT INTO MOVIMIENTO (num_transaccion_pk, Saldo, Tipo_Movimiento, Canal, Valor, Fecha_Hora, cuenta_a_la_que_pertenece) VALUES ('TRX-011', 500000, 'deposito', 'presencial', 500000, '2024-02-10 08:00:00+00', 'CTA-004');
INSERT INTO MOVIMIENTO (num_transaccion_pk, Saldo, Tipo_Movimiento, Canal, Valor, Fecha_Hora, cuenta_a_la_que_pertenece) VALUES ('TRX-012', 300000, 'retiro', 'cajero automático', 200000, '2024-03-20 16:00:00+00', 'CTA-004');
INSERT INTO MOVIMIENTO (num_transaccion_pk, Saldo, Tipo_Movimiento, Canal, Valor, Fecha_Hora, cuenta_a_la_que_pertenece) VALUES ('TRX-013', 100000, 'deposito', 'presencial', 100000, '2024-01-05 09:00:00+00', 'CTA-005');
INSERT INTO MOVIMIENTO (num_transaccion_pk, Saldo, Tipo_Movimiento, Canal, Valor, Fecha_Hora, cuenta_a_la_que_pertenece) VALUES ('TRX-014', 600000, 'deposito', 'aplicación móvil', 500000, '2024-06-01 11:00:00+00', 'CTA-004');
INSERT INTO MOVIMIENTO (num_transaccion_pk, Saldo, Tipo_Movimiento, Canal, Valor, Fecha_Hora, cuenta_a_la_que_pertenece) VALUES ('TRX-015', 400000, 'retiro', 'presencial', 200000, '2024-06-15 14:00:00+00', 'CTA-004');

-- =====================
-- REALIZA (asociado - movimiento)
-- =====================
INSERT INTO REALIZA VALUES ('2000001', 'TRX-001');
INSERT INTO REALIZA VALUES ('2000001', 'TRX-002');
INSERT INTO REALIZA VALUES ('2000001', 'TRX-003');
INSERT INTO REALIZA VALUES ('2000001', 'TRX-004');
INSERT INTO REALIZA VALUES ('2000004', 'TRX-005');
INSERT INTO REALIZA VALUES ('2000004', 'TRX-006');
INSERT INTO REALIZA VALUES ('2000004', 'TRX-007');
INSERT INTO REALIZA VALUES ('2000005', 'TRX-008');
INSERT INTO REALIZA VALUES ('2000005', 'TRX-009');
INSERT INTO REALIZA VALUES ('2000005', 'TRX-010');
INSERT INTO REALIZA VALUES ('2000006', 'TRX-011');
INSERT INTO REALIZA VALUES ('2000006', 'TRX-012');
INSERT INTO REALIZA VALUES ('2000009', 'TRX-013');
INSERT INTO REALIZA VALUES ('2000006', 'TRX-014');
INSERT INTO REALIZA VALUES ('2000006', 'TRX-015');

-- =====================
-- CREDITOS (4 estados distintos)
-- =====================
INSERT INTO CREDITO VALUES ('CRED-001', 'al día', '2023-01-15 08:00:00', 5000000, 5000000, 24, 1.5, '2023-02-15 08:00:00', 'libre inversión', 'AG01');
INSERT INTO CREDITO VALUES ('CRED-002', 'en mora', '2022-06-10 08:00:00', 8000000, 8000000, 36, 1.8, '2022-07-10 08:00:00', 'vivienda', 'AG02');
INSERT INTO CREDITO VALUES ('CRED-003', 'cancelado', '2021-03-20 08:00:00', 3000000, 3000000, 12, 1.2, '2021-04-20 08:00:00', 'educativo', 'AG03');
INSERT INTO CREDITO VALUES ('CRED-004', 'desembolsado', '2024-05-01 08:00:00', 15000000, 12000000, 48, 2.0, '2024-06-01 08:00:00', 'agropecuario', 'AG01');

-- =====================
-- SOLICITA (asociado - credito)
-- =====================
INSERT INTO SOLICITA VALUES ('2000001', 'CRED-001');
INSERT INTO SOLICITA VALUES ('2000004', 'CRED-002');
INSERT INTO SOLICITA VALUES ('2000005', 'CRED-003');
INSERT INTO SOLICITA VALUES ('2000006', 'CRED-004');

-- =====================
-- CODEUDORES (2)
-- =====================
INSERT INTO ES_CODEUDOR VALUES ('2000002', 'CRED-001', '2023-01-15');
INSERT INTO ES_CODEUDOR VALUES ('2000008', 'CRED-004', '2024-05-01');

-- =====================
-- CUOTAS (planes de pago parciales)
-- =====================
-- CRED-001 al día (6 cuotas pagadas de 24)
INSERT INTO CUOTAS VALUES ('PAG-001', 245000, 1, 'CRED-001', '2023-02-15', 'a tiempo');
INSERT INTO CUOTAS VALUES ('PAG-002', 245000, 2, 'CRED-001', '2023-03-15', 'a tiempo');
INSERT INTO CUOTAS VALUES ('PAG-003', 245000, 3, 'CRED-001', '2023-04-15', 'a tiempo');
INSERT INTO CUOTAS VALUES ('PAG-004', 245000, 4, 'CRED-001', '2023-05-20', 'pagado con mora');
INSERT INTO CUOTAS VALUES ('PAG-005', 245000, 5, 'CRED-001', '2023-06-15', 'a tiempo');
INSERT INTO CUOTAS VALUES ('PAG-006', 245000, 6, 'CRED-001', '2023-07-15', 'a tiempo');

-- CRED-002 en mora (4 cuotas, última sin pagar)
INSERT INTO CUOTAS VALUES ('PAG-007', 310000, 1, 'CRED-002', '2022-07-10', 'a tiempo');
INSERT INTO CUOTAS VALUES ('PAG-008', 310000, 2, 'CRED-002', '2022-08-15', 'pagado con mora');
INSERT INTO CUOTAS VALUES ('PAG-009', 310000, 3, 'CRED-002', '2022-09-10', 'a tiempo');
INSERT INTO CUOTAS VALUES ('PAG-010', 310000, 4, 'CRED-002', NULL, 'pendiente');

-- CRED-003 cancelado (12 cuotas todas pagadas)
INSERT INTO CUOTAS VALUES ('PAG-011', 260000, 1, 'CRED-003', '2021-04-20', 'a tiempo');
INSERT INTO CUOTAS VALUES ('PAG-012', 260000, 2, 'CRED-003', '2021-05-20', 'a tiempo');
INSERT INTO CUOTAS VALUES ('PAG-013', 260000, 3, 'CRED-003', '2021-06-20', 'a tiempo');
INSERT INTO CUOTAS VALUES ('PAG-014', 260000, 4, 'CRED-003', '2021-07-20', 'a tiempo');

-- CRED-004 desembolsado (2 cuotas pagadas)
INSERT INTO CUOTAS VALUES ('PAG-015', 380000, 1, 'CRED-004', '2024-06-01', 'a tiempo');
INSERT INTO CUOTAS VALUES ('PAG-016', 380000, 2, 'CRED-004', '2024-07-01', 'a tiempo');

-- =====================
-- ATIENDE (empleado - asociado)
-- =====================
INSERT INTO ATIENDE VALUES ('1000004', '2000001', '2023-01-15 09:00:00+00');
INSERT INTO ATIENDE VALUES ('1000004', '2000004', '2022-06-10 10:00:00+00');
INSERT INTO ATIENDE VALUES ('1000005', '2000005', '2021-03-20 09:00:00+00');
INSERT INTO ATIENDE VALUES ('1000006', '2000006', '2024-05-01 08:00:00+00');
INSERT INTO ATIENDE VALUES ('1000004', '2000009', '2022-04-18 11:00:00+00');
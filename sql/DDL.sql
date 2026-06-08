--  tablas que no son dependientes

create table CARGO (
  	cod_cargo_pk VARCHAR(20) NOT NULL,
  	Nombre VARCHAR(100) NOT NULL,
  	turno VARCHAR(50) NULL,
  	ventanilla_asignada VARCHAR(50) NULL,
  	presupuesto FLOAT NULL,
  	bono_gestion FLOAT NULL,
  	meta_mensual FLOAT NULL,
  	zona VARCHAR(50) NULL,
  	PRIMARY KEY (cod_cargo_pk)
);

create table AGENCIA (
	Codigo_pk VARCHAR(20) NOT NULL,
  	Telefono VARCHAR(20) NULL,
  	Municipio VARCHAR(100) NOT NULL,
  	Nombre VARCHAR(100) NOT NULL,
  	Fecha_apertura TIMESTAMP NULL,
  	Direccion VARCHAR(150) NULL,
  	PRIMARY KEY (Codigo_pk)
);

create table ASOCIADO (
  	cedula_pk VARCHAR(20) NOT NULL,
  	Nombres VARCHAR(100) NOT NULL,
  	Apellidos VARCHAR(100) NOT NULL,
  	Fecha_na DATE NOT NULL,
  	Telefono VARCHAR(20) NOT NULL,
  	Estado VARCHAR(30) NULL,
  	Fech_afil TIMESTAMP NULL,
  	Municipio VARCHAR(100) NULL,
  	correo VARCHAR(100) NULL,
  	Direccion VARCHAR(150) NULL,
	password VARCHAR(255) NULL,
    intentos_fallidos INTEGER DEFAULT 0,
    bloqueado BOOLEAN DEFAULT FALSE,
  	PRIMARY KEY (cedula_pk)
);

--  tablas que son dependientes

create table EMPLEADO (
	Cedula_pk VARCHAR(20) NOT NULL,
  	CodigoAgencia_fk VARCHAR(20) NOT NULL,
  	Tipo_labor VARCHAR(50) NULL,
  	Correo_corp VARCHAR(100) NULL,
  	Nombres VARCHAR(100) NOT NULL,
  	Apellidos VARCHAR(100) NOT NULL,
  	cod_cargo_fk VARCHAR(20) NOT NULL,
  	Fecha_Ingreso TIMESTAMP NULL,
  	Salario_base FLOAT NULL,
  	Estado_Laboral VARCHAR(30) NULL,
	password VARCHAR(255) NULL,
    intentos_fallidos INTEGER DEFAULT 0,
    bloqueado BOOLEAN DEFAULT FALSE,
  	PRIMARY KEY (Cedula_pk),
	-- es dependiente de agencia y cargo
  	CONSTRAINT fk_empl_agencia FOREIGN KEY (CodigoAgencia_fk) REFERENCES AGENCIA(Codigo_pk),
  	CONSTRAINT fk_empl_cargo FOREIGN KEY (cod_cargo_fk) REFERENCES CARGO(cod_cargo_pk)
);

create table CREDITO (
  	Num_radicado_pk VARCHAR(30) NOT NULL,
  	Estado VARCHAR(30) NULL,
  	Fecha_aprov TIMESTAMP NULL,
  	valor_solicitado NUMERIC(15, 2) NOT NULL,
  	valor_aprovado NUMERIC(15, 2) NULL,
  	plazo_meses INT NULL,
  	Tasa_interes_m NUMERIC(5, 2) NULL,
  	Fech_prim_ven TIMESTAMP NULL,
  	Linea_credito VARCHAR(50) NULL,
  	codigo_agencia_fk VARCHAR(20) NOT NULL,
  	PRIMARY KEY (Num_radicado_pk),
	 -- es dependiente de agencia
  	CONSTRAINT fk_cred_agencia FOREIGN KEY (codigo_agencia_fk) REFERENCES AGENCIA(Codigo_pk)
);

create table CUENTA_AHORRO (
  	Numero_pk VARCHAR(30) NOT NULL,
  	CodigoAgencia_fk VARCHAR(20) NOT NULL,
  	cedula_asociado_fk VARCHAR(20) NOT NULL,
  	Fecha_apertura TIMESTAMP NULL,
  	Estado VARCHAR(30) NULL,
  	PRIMARY KEY (Numero_pk),
	-- es dependiente de agencia y asociado
  	CONSTRAINT fk_cuenta_agencia FOREIGN KEY (CodigoAgencia_fk) REFERENCES AGENCIA(Codigo_pk),
  	CONSTRAINT fk_cuenta_asociado FOREIGN KEY (cedula_asociado_fk) REFERENCES ASOCIADO(cedula_pk)
);

create table ASOCIADO_FUND (
  	cedula_pk VARCHAR(20) NOT NULL,
  	Num_acta_fundacional VARCHAR(50) NOT NULL,
  	Ano_reconocimiento INTEGER NULL,
  	Descripcion_beneficios TEXT NULL,
  	Fecha_firma TIMESTAMP NULL,
  	PRIMARY KEY (cedula_pk),
	-- es dependiente de asociado
  	CONSTRAINT fk_asociadofund_asociado FOREIGN KEY (cedula_pk) REFERENCES ASOCIADO(cedula_pk)
);

create table BENEFICIARIO (
  	cedula_pk VARCHAR(20) NOT NULL,
  	cedulaAsociado_fk VARCHAR(20) NOT NULL,
  	Parentesco VARCHAR(50) NULL,
  	Nombre_Completo VARCHAR(150) NOT NULL,
  	Porcentaje_participacion FLOAT NULL,
  	Telefono VARCHAR(20) NULL,
  	PRIMARY KEY (cedula_pk),
	-- es dependiente de asociado
  	CONSTRAINT fk_benef_asociado FOREIGN KEY (cedulaAsociado_fk) REFERENCES ASOCIADO(cedula_pk)
);

-- relaciones (1:1)

create table CUOTAS (
  	id_pago_pk VARCHAR(30) NOT NULL,
  	Valor_pagado FLOAT NOT NULL,
  	Num_cuota INTEGER NOT NULL,
  	Num_radicado_fk VARCHAR(30) NOT NULL,
  	Fech_pago DATE NULL,
  	Estado_pago VARCHAR(30) NULL,
  	PRIMARY KEY (id_pago_pk),
	-- es dependiente de credito
  	CONSTRAINT fk_cuotas_credito FOREIGN KEY (Num_radicado_fk) REFERENCES CREDITO(Num_radicado_pk)
);

create table MOVIMIENTO (
	num_transaccion_pk VARCHAR(30) NOT NULL,
	Saldo FLOAT NOT NULL,
  	Tipo_Movimiento VARCHAR(50) NOT NULL,
  	Canal VARCHAR(50) NULL,
  	Valor FLOAT NOT NULL,
  	Fecha_Hora TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
  	-- se usa para registrar el momento exacto cuando se realiza el movimiento
	Numero_cuenta_aporte VARCHAR(30) NULL,
  	cuenta_a_la_que_pertenece VARCHAR(30) NULL,
  	cuenta_origen VARCHAR(30) NULL,
  	cuenta_destino VARCHAR(30) NULL,
  	PRIMARY KEY (num_transaccion_pk)
);

-- relaaciones (N:M)

create table SUPERVISA (
  	CedulaSupervisor_fk VARCHAR(20) NOT NULL,
  	CedulaSubordinado_fk VARCHAR(20) NOT NULL,
	--evita duplicar la relacion supervisor - empleado
  	PRIMARY KEY (CedulaSupervisor_fk, CedulaSubordinado_fk),
  	CONSTRAINT fk_supervisa_supervisor FOREIGN KEY (CedulaSupervisor_fk) REFERENCES EMPLEADO(Cedula_pk),
  	CONSTRAINT fk_supervisa_subordinado FOREIGN KEY (CedulaSubordinado_fk) REFERENCES EMPLEADO(Cedula_pk)
);

create table SOLICITA (
  	CedulaAsociado_fk VARCHAR(20) NOT NULL,
	Num_radicadoCredito_fk VARCHAR(30) NOT NULL,
	--evita duplicar un asociado en el mismo credito
  	PRIMARY KEY (CedulaAsociado_fk, Num_radicadoCredito_fk),
  	CONSTRAINT fk_solicita_asociado FOREIGN KEY (CedulaAsociado_fk) REFERENCES ASOCIADO(cedula_pk),
  	CONSTRAINT fk_solicita_credito FOREIGN KEY (Num_radicadoCredito_fk) REFERENCES CREDITO(Num_radicado_pk)
);

create table ES_CODEUDOR (
  	CedulaAsociado_fk VARCHAR(20) NOT NULL,
  	Num_radicadoCredito_fk VARCHAR(30) NOT NULL,
  	Fecha_Firma DATE NOT NULL,
	-- registra al asociado como codeudor unico del credito
  	PRIMARY KEY (CedulaAsociado_fk, Num_radicadoCredito_fk),
  	CONSTRAINT fk_codeudor_asociado FOREIGN KEY (CedulaAsociado_fk) REFERENCES ASOCIADO(cedula_pk),
  	CONSTRAINT fk_codeudor_credito FOREIGN KEY (Num_radicadoCredito_fk) REFERENCES CREDITO(Num_radicado_pk)
);

create table ATIENDE (
  	cedulaEmpleado_fk VARCHAR(20) NOT NULL,
  	cedulaAsociado_fk VARCHAR(20) NOT NULL,
  	Fecha_atencion TIMESTAMP WITH TIME ZONE NOT NULL,
	-- permite varias atenciones en fechas distintas
  	PRIMARY KEY (cedulaEmpleado_fk, cedulaAsociado_fk, Fecha_atencion),
  	CONSTRAINT fk_atiende_empleado FOREIGN KEY (cedulaEmpleado_fk) REFERENCES EMPLEADO(Cedula_pk),
	CONSTRAINT fk_atiende_asociado FOREIGN KEY (cedulaAsociado_fk) REFERENCES ASOCIADO(cedula_pk)
);

create table REALIZA (
  	cedulaAsociado_fk VARCHAR(20) NOT NULL,
  	num_transaccionMov_fk VARCHAR(30) NOT NULL,
  	PRIMARY KEY (cedulaAsociado_fk, num_transaccionMov_fk),
	-- une de forma unica al asociado con su transicion
  	CONSTRAINT fk_realiza_asociado FOREIGN KEY (cedulaAsociado_fk) REFERENCES ASOCIADO(cedula_pk),
  	CONSTRAINT fk_realiza_movimiento FOREIGN KEY (num_transaccionMov_fk) REFERENCES MOVIMIENTO(num_transaccion_pk)
);

--Tabla para solicitudes del asociado que quiere cambiar algunos datos
CREATE TABLE SOLICITUD_ACTUALIZACION (
    id_solicitud SERIAL PRIMARY KEY,
    cedula_asociado_fk VARCHAR(20) NOT NULL,
    telefono_nuevo VARCHAR(20),
    correo_nuevo VARCHAR(100),
    direccion_nueva VARCHAR(150),
    estado VARCHAR(20) DEFAULT 'pendiente',

    FOREIGN KEY (cedula_asociado_fk)
        REFERENCES ASOCIADO(cedula_pk)
);

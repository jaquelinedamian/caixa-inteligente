from app import db
from werkzeug.security import generate_password_hash, check_password_hash


class Usuario(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    telefone = db.Column(db.String(30), nullable=True)
    senha_hash = db.Column(db.String(255), nullable=False)
    foto = db.Column(db.String(255), nullable=True)
    criado_em = db.Column(db.DateTime, server_default=db.func.now())

    dispositivos = db.relationship(
        "Dispositivo",
        backref="usuario",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)

    def verificar_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)


class Dispositivo(db.Model):
    __tablename__ = "dispositivos"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)

    nome = db.Column(db.String(120), nullable=False)
    bluetooth_id = db.Column(db.String(120), nullable=True)
    status = db.Column(db.String(30), default="conectado")

    criado_em = db.Column(db.DateTime, server_default=db.func.now())
    conectado_em = db.Column(db.DateTime, nullable=True)

    tratamentos = db.relationship(
        "Tratamento",
        backref="dispositivo",
        lazy=True,
        cascade="all, delete-orphan"
    )

    alertas = db.relationship(
        "ConfiguracaoAlerta",
        backref="dispositivo",
        lazy=True,
        cascade="all, delete-orphan"
    )

    registros = db.relationship(
        "RegistroDose",
        backref="dispositivo",
        lazy=True,
        cascade="all, delete-orphan"
    )


class Tratamento(db.Model):
    __tablename__ = "tratamentos"

    id = db.Column(db.Integer, primary_key=True)
    dispositivo_id = db.Column(db.Integer, db.ForeignKey("dispositivos.id"), nullable=False)

    nome = db.Column(db.String(120), nullable=False)
    tipo = db.Column(db.String(50), nullable=True)
    doses_por_ciclo = db.Column(db.Integer, nullable=True)

    data_inicio = db.Column(db.Date, nullable=True)
    data_fim = db.Column(db.Date, nullable=True)
    uso_continuo = db.Column(db.Boolean, default=False)
    ativo = db.Column(db.Boolean, default=True)

    horarios = db.relationship(
        "HorarioMedicacao",
        backref="tratamento",
        lazy=True,
        cascade="all, delete-orphan"
    )


class HorarioMedicacao(db.Model):
    __tablename__ = "horarios_medicacao"

    id = db.Column(db.Integer, primary_key=True)
    tratamento_id = db.Column(db.Integer, db.ForeignKey("tratamentos.id"), nullable=False)

    horario = db.Column(db.Time, nullable=False)
    ativo = db.Column(db.Boolean, default=True)

    registros = db.relationship(
        "RegistroDose",
        backref="horario_medicacao",
        lazy=True
    )


class ConfiguracaoAlerta(db.Model):
    __tablename__ = "configuracoes_alerta"

    id = db.Column(db.Integer, primary_key=True)
    dispositivo_id = db.Column(db.Integer, db.ForeignKey("dispositivos.id"), nullable=False)

    mensagem = db.Column(db.Boolean, default=True)
    sonoro = db.Column(db.Boolean, default=True)
    led = db.Column(db.Boolean, default=True)
    vibratorio = db.Column(db.Boolean, default=True)


class RegistroDose(db.Model):
    __tablename__ = "registros_dose"

    id = db.Column(db.Integer, primary_key=True)

    dispositivo_id = db.Column(db.Integer, db.ForeignKey("dispositivos.id"), nullable=False)
    horario_id = db.Column(db.Integer, db.ForeignKey("horarios_medicacao.id"), nullable=True)

    data_prevista = db.Column(db.Date, nullable=False)
    horario_previsto = db.Column(db.Time, nullable=False)
    aberto_em = db.Column(db.DateTime, nullable=True)

    status = db.Column(db.String(30), default="pendente")
    # pendente | tomada | atrasada | nao_tomada

    criado_em = db.Column(db.DateTime, server_default=db.func.now())
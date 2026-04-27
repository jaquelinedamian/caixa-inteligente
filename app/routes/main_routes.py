from datetime import datetime, date, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, session
from app import db
from app.models import (
    Usuario,
    Dispositivo,
    Tratamento,
    HorarioMedicacao,
    ConfiguracaoAlerta,
    RegistroDose
)

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    return render_template("pages/index.html", page_title="Início")


@main_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        senha = request.form.get("senha")

        usuario = Usuario.query.filter_by(email=email).first()

        if not usuario or not usuario.verificar_senha(senha):
            return "E-mail ou senha inválidos."

        session["usuario_id"] = usuario.id
        session["usuario_nome"] = usuario.nome

        return redirect(url_for("main.home"))

    return render_template("pages/login.html", page_title="Login")


@main_bp.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        nome = request.form.get("nome")
        email = request.form.get("email")
        telefone = request.form.get("telefone")
        senha = request.form.get("senha")

        usuario_existente = Usuario.query.filter_by(email=email).first()

        if usuario_existente:
            return "Este e-mail já está cadastrado."

        usuario = Usuario(nome=nome, email=email, telefone=telefone)
        usuario.set_senha(senha)

        db.session.add(usuario)
        db.session.commit()

        return redirect(url_for("main.login"))

    return render_template("pages/cadastro.html", page_title="Cadastro")


@main_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("main.login"))


@main_bp.route("/home")
def home():
    if not session.get("usuario_id"):
        return redirect(url_for("main.login"))

    dispositivos = Dispositivo.query.filter_by(usuario_id=session["usuario_id"]).all()

    return render_template(
        "pages/home.html",
        page_title="Home",
        usuario_nome=session.get("usuario_nome"),
        dispositivos=dispositivos
    )


@main_bp.route("/dispositivos")
def dispositivos():
    if not session.get("usuario_id"):
        return redirect(url_for("main.login"))

    dispositivos = Dispositivo.query.filter_by(usuario_id=session["usuario_id"]).all()

    return render_template(
        "pages/dispositivos.html",
        page_title="Dispositivos",
        dispositivos=dispositivos
    )


@main_bp.route("/configuracao-dispositivo", methods=["GET", "POST"])
@main_bp.route("/configuracao-dispositivo/<int:dispositivo_id>", methods=["GET", "POST"])
def configuracao_dispositivo(dispositivo_id=None):
    if not session.get("usuario_id"):
        return redirect(url_for("main.login"))

    dispositivo = None

    if dispositivo_id:
        dispositivo = Dispositivo.query.filter_by(
            id=dispositivo_id,
            usuario_id=session["usuario_id"]
        ).first_or_404()

    if request.method == "POST":
        nome_dispositivo = request.form.get("nome_dispositivo")
        bluetooth_id = request.form.get("bluetooth_id")

        nome_tratamento = request.form.get("nome_tratamento")
        tipo_tratamento = request.form.get("tipo_tratamento")
        doses_por_ciclo = request.form.get("doses_por_ciclo")

        data_inicio = request.form.get("data_inicio")
        data_fim = request.form.get("data_fim")

        uso_continuo = request.form.get("uso_continuo") == "on"
        horarios = request.form.getlist("horarios[]")

        alerta_mensagem = request.form.get("alerta_mensagem") == "on"
        alerta_sonoro = request.form.get("alerta_sonoro") == "on"
        alerta_led = request.form.get("alerta_led") == "on"
        alerta_vibratorio = request.form.get("alerta_vibratorio") == "on"

        if not nome_dispositivo:
            return "Nome do dispositivo é obrigatório."

        if not nome_tratamento:
            return "Nome do tratamento é obrigatório."

        if not horarios:
            return "Informe pelo menos um horário."

        if dispositivo:
            dispositivo.nome = nome_dispositivo
            dispositivo.bluetooth_id = bluetooth_id
            dispositivo.status = "conectado"
        else:
            dispositivo = Dispositivo(
                usuario_id=session["usuario_id"],
                nome=nome_dispositivo,
                bluetooth_id=bluetooth_id,
                status="conectado"
            )
            db.session.add(dispositivo)
            db.session.flush()

        tratamento = dispositivo.tratamentos[0] if dispositivo.tratamentos else None

        if tratamento:
            tratamento.nome = nome_tratamento
            tratamento.tipo = tipo_tratamento
            tratamento.doses_por_ciclo = int(doses_por_ciclo) if doses_por_ciclo else None
            tratamento.data_inicio = datetime.strptime(data_inicio, "%Y-%m-%d").date() if data_inicio else None
            tratamento.data_fim = datetime.strptime(data_fim, "%Y-%m-%d").date() if data_fim else None
            tratamento.uso_continuo = uso_continuo

            for horario_antigo in tratamento.horarios:
                db.session.delete(horario_antigo)
        else:
            tratamento = Tratamento(
                dispositivo_id=dispositivo.id,
                nome=nome_tratamento,
                tipo=tipo_tratamento,
                doses_por_ciclo=int(doses_por_ciclo) if doses_por_ciclo else None,
                data_inicio=datetime.strptime(data_inicio, "%Y-%m-%d").date() if data_inicio else None,
                data_fim=datetime.strptime(data_fim, "%Y-%m-%d").date() if data_fim else None,
                uso_continuo=uso_continuo
            )
            db.session.add(tratamento)
            db.session.flush()

        for horario in horarios:
            if horario:
                horario_obj = HorarioMedicacao(
                    tratamento_id=tratamento.id,
                    horario=datetime.strptime(horario, "%H:%M").time()
                )
                db.session.add(horario_obj)

        alerta = ConfiguracaoAlerta.query.filter_by(
            dispositivo_id=dispositivo.id
        ).first()

        if alerta:
            alerta.mensagem = alerta_mensagem
            alerta.sonoro = alerta_sonoro
            alerta.led = alerta_led
            alerta.vibratorio = alerta_vibratorio
        else:
            alerta = ConfiguracaoAlerta(
                dispositivo_id=dispositivo.id,
                mensagem=alerta_mensagem,
                sonoro=alerta_sonoro,
                led=alerta_led,
                vibratorio=alerta_vibratorio
            )
            db.session.add(alerta)

        db.session.commit()

        return redirect(url_for("main.dispositivos"))

    return render_template(
        "pages/configuracao-dispositivo.html",
        page_title="Configuração",
        dispositivo=dispositivo
    )


@main_bp.route("/deletar-dispositivo/<int:dispositivo_id>", methods=["POST"])
def deletar_dispositivo(dispositivo_id):
    if not session.get("usuario_id"):
        return redirect(url_for("main.login"))

    dispositivo = Dispositivo.query.filter_by(
        id=dispositivo_id,
        usuario_id=session["usuario_id"]
    ).first_or_404()

    for registro in dispositivo.registros:
        db.session.delete(registro)

    for tratamento in dispositivo.tratamentos:
        for horario in tratamento.horarios:
            db.session.delete(horario)

        db.session.delete(tratamento)

    alerta = ConfiguracaoAlerta.query.filter_by(
        dispositivo_id=dispositivo.id
    ).first()

    if alerta:
        db.session.delete(alerta)

    db.session.delete(dispositivo)
    db.session.commit()

    return redirect(url_for("main.dispositivos"))


@main_bp.route("/horarios")
def horarios():
    if not session.get("usuario_id"):
        return redirect(url_for("main.login"))

    dispositivos = Dispositivo.query.filter_by(usuario_id=session["usuario_id"]).all()

    return render_template(
        "pages/horarios.html",
        page_title="Horários",
        dispositivos=dispositivos
    )


@main_bp.route("/historico")
def historico():
    if not session.get("usuario_id"):
        return redirect(url_for("main.login"))

    registros = (
        RegistroDose.query
        .join(Dispositivo)
        .filter(Dispositivo.usuario_id == session["usuario_id"])
        .order_by(RegistroDose.criado_em.desc())
        .all()
    )

    return render_template(
        "pages/historico.html",
        page_title="Histórico",
        registros=registros
    )


@main_bp.route("/perfil")
def perfil():
    if not session.get("usuario_id"):
        return redirect(url_for("main.login"))

    usuario = Usuario.query.get(session["usuario_id"])

    return render_template(
        "pages/perfil.html",
        page_title="Perfil",
        usuario=usuario
    )


@main_bp.route("/simular-arduino")
def simular_arduino():
    if not session.get("usuario_id"):
        return redirect(url_for("main.login"))

    dispositivos = Dispositivo.query.filter_by(usuario_id=session["usuario_id"]).all()

    return render_template(
        "pages/simular-arduino.html",
        page_title="Simular Arduino",
        dispositivos=dispositivos
    )


@main_bp.route("/simular-abertura/<int:dispositivo_id>", methods=["POST"])
def simular_abertura(dispositivo_id):
    if not session.get("usuario_id"):
        return redirect(url_for("main.login"))

    dispositivo = Dispositivo.query.filter_by(
        id=dispositivo_id,
        usuario_id=session["usuario_id"]
    ).first_or_404()

    agora = datetime.now()
    hoje = date.today()

    horarios = []

    for tratamento in dispositivo.tratamentos:
        for horario in tratamento.horarios:
            if horario.ativo:
                horarios.append(horario)

    if not horarios:
        return "Este dispositivo ainda não possui horários cadastrados."

    horario_mais_proximo = min(
        horarios,
        key=lambda h: abs(datetime.combine(hoje, h.horario) - agora)
    )

    horario_previsto_dt = datetime.combine(hoje, horario_mais_proximo.horario)
    minutos = (agora - horario_previsto_dt).total_seconds() / 60

    if -15 <= minutos <= 15:
        status = "tomada"
    elif minutos > 15:
        status = "atrasada"
    else:
        status = "fora_do_horario"

    registro = RegistroDose(
        dispositivo_id=dispositivo.id,
        horario_id=horario_mais_proximo.id,
        data_prevista=hoje,
        horario_previsto=horario_mais_proximo.horario,
        aberto_em=agora,
        status=status
    )

    db.session.add(registro)
    db.session.commit()

    return redirect(url_for("main.historico"))


@main_bp.route("/init-db")
def init_db():
    db.create_all()
    return "Banco criado com sucesso."




@main_bp.route("/gerar-dados-teste")
def gerar_dados_teste():
    if not session.get("usuario_id"):
        return redirect(url_for("main.login"))

    usuario_id = session["usuario_id"]

    dispositivo = Dispositivo(
        usuario_id=usuario_id,
        nome="Caixa Inteligente - Teste",
        bluetooth_id="CX-BT-TESTE-001",
        status="conectado"
    )

    db.session.add(dispositivo)
    db.session.flush()

    tratamento = Tratamento(
        dispositivo_id=dispositivo.id,
        nome="Antibiótico 12h - Ciclo Completo",
        tipo="12h",
        doses_por_ciclo=28,
        data_inicio=date(2026, 4, 1),
        data_fim=date(2026, 4, 14),
        uso_continuo=False
    )

    db.session.add(tratamento)
    db.session.flush()

    horarios_base = ["08:00", "20:00"]
    horarios_objs = []

    for horario_texto in horarios_base:
        horario_obj = HorarioMedicacao(
            tratamento_id=tratamento.id,
            horario=datetime.strptime(horario_texto, "%H:%M").time(),
            ativo=True
        )

        db.session.add(horario_obj)
        horarios_objs.append(horario_obj)

    alerta = ConfiguracaoAlerta(
        dispositivo_id=dispositivo.id,
        mensagem=True,
        sonoro=True,
        led=True,
        vibratorio=True
    )

    db.session.add(alerta)
    db.session.flush()

    atrasadas = {
        "2026-04-03 08:00": 35,
        "2026-04-06 20:00": 48,
        "2026-04-10 08:00": 22,
        "2026-04-12 20:00": 65
    }

    fora_do_horario = {
        "2026-04-05 08:00": -90,
        "2026-04-09 20:00": -120
    }

    for dia in range(1, 15):
        data_prevista = date(2026, 4, dia)

        for horario_obj in horarios_objs:
            chave = f"{data_prevista.strftime('%Y-%m-%d')} {horario_obj.horario.strftime('%H:%M')}"

            horario_previsto_dt = datetime.combine(data_prevista, horario_obj.horario)

            if chave in atrasadas:
                minutos = atrasadas[chave]
                status = "atrasada"
            elif chave in fora_do_horario:
                minutos = fora_do_horario[chave]
                status = "fora_do_horario"
            else:
                minutos = 5
                status = "tomada"

            aberto_em = horario_previsto_dt.replace(
                minute=horario_previsto_dt.minute
            )

            aberto_em = aberto_em + timedelta(minutes=minutos)

            registro = RegistroDose(
                dispositivo_id=dispositivo.id,
                horario_id=horario_obj.id,
                data_prevista=data_prevista,
                horario_previsto=horario_obj.horario,
                aberto_em=aberto_em,
                status=status
            )

            db.session.add(registro)

    db.session.commit()

    return redirect(url_for("main.home"))


@main_bp.route("/recuperar-senha")
def recuperar_senha():
    return render_template("pages/recuperar-senha.html", page_title="Recuperar senha")


    @main.route("/")
@main.route("/pagina-inicial")
def pagina_inicial():
    return render_template("pages/home.html", page_title="Página Inicial")


@main.route("/como-funciona")
def como_funciona():
    return render_template("pages/como-funciona.html", page_title="Como funciona")


@main.route("/suporte")
def suporte():
    return render_template("pages/suporte.html", page_title="Fale conosco")
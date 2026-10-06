from flask import Blueprint, flash, redirect, render_template, request, url_for

from models import acomodacao

# EXEMPLO:
# Cada grupo deverá substituir "records" pela entidade principal
# do seu próprio projeto, como livros, pacientes ou produtos.
# Para cada entidade nova: um arquivo em models/ e um em routes/.
records_bp = Blueprint("acomodacoes", __name__, url_prefix="/sistema/acomodacoes")


@records_bp.route("/")
def listar_registros():
    return render_template(
        "acomodacoes/lista.html",
        records=acomodacoes.listar_registros()
    )


@records_bp.route("/novo", methods=["GET", "POST"])
def novo_registro():
    if request.method == "POST":
        id_anfitriao = request.form["id_anfitriao"].strip()
        id_endereco = request.form["id_endereco"].strip()

        titulo = request.form["titulo"].strip()
        descricao = request.form.get("descricao", "").strip()
        tipo = request.form["tipo"].strip()

        area_m2 = request.form["area_m2"].strip()
        capacidade = request.form["capacidade"].strip()
        qtd_quartos = request.form.get("qtd_quartos", "1").strip()
        qtd_banheiros = request.form.get("qtd_banheiros", "1").strip()

        aceita_pet = request.form.get("aceita_pet", "0").strip()
        taxa_pet = request.form.get("taxa_pet", "0.00").strip()

        preco_noite = request.form["preco_noite"].strip()
        status = request.form.get("status", "DISPONIVEL").strip()

        # Validações básicas
        if not titulo:
            flash("Informe um título para a acomodação.", "danger")
            return render_template(
                "acomodacoes/form.html",
                record=request.form
            )

        if not tipo:
            flash("Informe o tipo da acomodação.", "danger")
            return render_template(
                "acomodacoes/form.html",
                record=request.form
            )

        try:
            id_anfitriao = int(id_anfitriao)
            id_endereco = int(id_endereco)

            area_m2 = float(area_m2)
            capacidade = int(capacidade)
            qtd_quartos = int(qtd_quartos)
            qtd_banheiros = int(qtd_banheiros)

            aceita_pet = int(aceita_pet)
            taxa_pet = float(taxa_pet)
            preco_noite = float(preco_noite)

        except ValueError:
            flash("Informe valores numéricos válidos.", "danger")
            return render_template(
                "acomodacoes/form.html",
                record=request.form
            )

        if area_m2 <= 0:
            flash("A área deve ser maior que zero.", "danger")
            return render_template(
                "acomodacoes/form.html",
                record=request.form
            )

        if capacidade <= 0:
            flash("A capacidade deve ser maior que zero.", "danger")
            return render_template(
                "acomodacoes/form.html",
                record=request.form
            )

        if qtd_quartos < 0:
            flash("A quantidade de quartos não pode ser negativa.", "danger")
            return render_template(
                "acomodacoes/form.html",
                record=request.form
            )

        if qtd_banheiros < 0:
            flash("A quantidade de banheiros não pode ser negativa.", "danger")
            return render_template(
                "acomodacoes/form.html",
                record=request.form
            )

        if aceita_pet not in (0, 1):
            flash("O campo aceita_pet deve ser 0 ou 1.", "danger")
            return render_template(
                "acomodacoes/form.html",
                record=request.form
            )

        if taxa_pet < 0:
            flash("A taxa para pets não pode ser negativa.", "danger")
            return render_template(
                "acomodacoes/form.html",
                record=request.form
            )

        if preco_noite < 0:
            flash("O preço da diária não pode ser negativo.", "danger")
            return render_template(
                "acomodacoes/form.html",
                record=request.form
            )

        acomodacoes.criar_registro(
            id_anfitriao,
            id_endereco,
            titulo,
            descricao,
            tipo,
            area_m2,
            capacidade,
            qtd_quartos,
            qtd_banheiros,
            aceita_pet,
            taxa_pet,
            preco_noite,
            status
        )

        flash("Acomodação criada com sucesso.", "success")
        return redirect(url_for("acomodacoes.listar_registros"))

    return render_template(
        "acomodacoes/form.html",
        record=None
    )


@records_bp.route("/<int:record_id>/editar", methods=["GET", "POST"])
def editar_registro(record_id):
    record = acomodacoes.buscar_registro(record_id)

    if record is None:
        flash("Acomodação não encontrada.", "danger")
        return redirect(url_for("acomodacoes.listar_registros"))

    if request.method == "POST":
        id_anfitriao = request.form["id_anfitriao"].strip()
        id_endereco = request.form["id_endereco"].strip()

        titulo = request.form["titulo"].strip()
        descricao = request.form.get("descricao", "").strip()
        tipo = request.form["tipo"].strip()

        area_m2 = request.form["area_m2"].strip()
        capacidade = request.form["capacidade"].strip()
        qtd_quartos = request.form.get("qtd_quartos", "1").strip()
        qtd_banheiros = request.form.get("qtd_banheiros", "1").strip()

        aceita_pet = request.form.get("aceita_pet", "0").strip()
        taxa_pet = request.form.get("taxa_pet", "0.00").strip()

        preco_noite = request.form["preco_noite"].strip()
        status = request.form.get("status", "DISPONIVEL").strip()

        if not titulo:
            flash("Informe um título para a acomodação.", "danger")
            return render_template(
                "acomodacoes/form.html",
                record=request.form
            )

        if not tipo:
            flash("Informe o tipo da acomodação.", "danger")
            return render_template(
                "acomodacoes/form.html",
                record=request.form
            )

        try:
            id_anfitriao = int(id_anfitriao)
            id_endereco = int(id_endereco)

            area_m2 = float(area_m2)
            capacidade = int(capacidade)
            qtd_quartos = int(qtd_quartos)
            qtd_banheiros = int(qtd_banheiros)

            aceita_pet = int(aceita_pet)
            taxa_pet = float(taxa_pet)
            preco_noite = float(preco_noite)

        except ValueError:
            flash("Informe valores numéricos válidos.", "danger")
            return render_template(
                "acomodacoes/form.html",
                record=request.form
            )

        if area_m2 <= 0:
            flash("A área deve ser maior que zero.", "danger")
            return render_template(
                "acomodacoes/form.html",
                record=request.form
            )

        if capacidade <= 0:
            flash("A capacidade deve ser maior que zero.", "danger")
            return render_template(
                "acomodacoes/form.html",
                record=request.form
            )

        if qtd_quartos < 0 or qtd_banheiros < 0:
            flash("Quartos e banheiros não podem ser negativos.", "danger")
            return render_template(
                "acomodacoes/form.html",
                record=request.form
            )

        if aceita_pet not in (0, 1):
            flash("O campo aceita_pet deve ser 0 ou 1.", "danger")
            return render_template(
                "acomodacoes/form.html",
                record=request.form
            )

        if taxa_pet < 0:
            flash("A taxa para pets não pode ser negativa.", "danger")
            return render_template(
                "acomodacoes/form.html",
                record=request.form
            )

        if preco_noite < 0:
            flash("O preço da diária não pode ser negativo.", "danger")
            return render_template(
                "acomodacoes/form.html",
                record=request.form
            )

        acomodacoes.atualizar_registro(
            record_id,
            id_anfitriao,
            id_endereco,
            titulo,
            descricao,
            tipo,
            area_m2,
            capacidade,
            qtd_quartos,
            qtd_banheiros,
            aceita_pet,
            taxa_pet,
            preco_noite,
            status
        )

        flash("Acomodação atualizada com sucesso.", "success")
        return redirect(url_for("acomodacoes.listar_registros"))

    return render_template(
        "acomodacoes/form.html",
        record=record
    )


@records_bp.route("/<int:record_id>/excluir", methods=["POST"])
def excluir_registro(record_id):
    acomodacoes.excluir_registro(record_id)

    flash("Acomodação excluída.", "success")
    return redirect(url_for("acomodacoes.listar_registros"))

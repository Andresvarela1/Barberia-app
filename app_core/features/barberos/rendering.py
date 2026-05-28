import logging

import streamlit as st

from app_core.auth import registrar
from app_core.db import safe_execute
from app_core.services.availability_service import listar_usuarios_barberos
from design_system import (
    render_alert,
    render_divider,
    render_panel_empty_state,
    render_panel_header,
    render_subsection_title,
)

logger = logging.getLogger("barberia_app")


def render_barberos_section(
    *,
    barberia_id,
    db_ok,
    meta,
    no_context_message,
    no_db_message="Gestión de equipo no disponible sin base de datos",
):
    render_panel_header(
        "Equipo",
        "Crea y administra los barberos asociados a esta barbería.",
        eyebrow="Gestión",
        meta=meta,
    )

    if not db_ok:
        render_alert(no_db_message, alert_type="info", title="Modo demo")
        return

    if not barberia_id:
        render_alert(no_context_message, alert_type="info", title="Contexto requerido")
        return

    st.markdown(
        """<style>
.barbero-card {
    background: #1a1a1a;
    border: 1px solid rgba(197,159,85,0.2);
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 16px;
}
.barbero-avatar {
    width: 48px;
    height: 48px;
    border-radius: 50%;
    background: linear-gradient(135deg, #c5a028, #8a6e17);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 22px;
    font-weight: 700;
    color: #080808;
    flex-shrink: 0;
    text-transform: uppercase;
}
.barbero-info { flex: 1; }
.barbero-nombre { font-size: 17px; font-weight: 600; color: #f5f0e8; margin: 0; }
.barbero-rol { font-size: 13px; color: rgba(197,159,85,0.8); margin: 2px 0 0 0; }
</style>""",
        unsafe_allow_html=True,
    )

    render_subsection_title("Agregar barbero")
    render_alert(
        "Cada nuevo barbero queda disponible de inmediato en agenda y reservas.",
        alert_type="info",
        title="Alta rápida",
    )

    with st.form("form_crear_barbero_equipo", clear_on_submit=True):
        col_u, col_p = st.columns(2)

        with col_u:
            nuevo_usuario = st.text_input("Nombre de usuario", placeholder="Ej: carlos")

        with col_p:
            nueva_password = st.text_input("Contraseña", type="password")

        crear_btn = st.form_submit_button("Agregar al equipo", use_container_width=True, type="primary")

    if crear_btn:
        if not nuevo_usuario or not nuevo_usuario.strip():
            render_alert("El nombre de usuario es obligatorio.", alert_type="error", title="Revisa los datos")
        elif not nueva_password or len(nueva_password) < 4:
            render_alert("La contraseña debe tener al menos 4 caracteres.", alert_type="error", title="Revisa los datos")
        else:
            ok = registrar(nuevo_usuario.strip(), nueva_password, "BARBERO", barberia_id=barberia_id)
            if ok:
                render_alert(
                    f"Barbero '{nuevo_usuario}' agregado al equipo. Ya está disponible para asignaciones.",
                    alert_type="success",
                    title="Equipo actualizado",
                )
                st.rerun()

    render_divider()
    render_subsection_title("Equipo registrado")

    with st.spinner("Cargando equipo..."):
        barberos_data = listar_usuarios_barberos(barberia_id)

    if not barberos_data:
        render_panel_empty_state(
            "Sin barberos aún",
            "Usa el formulario de arriba para agregar el primer barbero al equipo y habilitarlo en agenda y reservas.",
        )
        return

    for row in barberos_data:
        bid_barber, bname = row[0], row[1]
        inicial = bname[0].upper() if bname else "B"

        st.markdown(
            f'<div class="barbero-card">'
            f'<div class="barbero-avatar">{inicial}</div>'
            f'<div class="barbero-info">'
            f'<p class="barbero-nombre">{bname}</p>'
            f'<p class="barbero-rol">Barbero</p>'
            f"</div></div>",
            unsafe_allow_html=True,
        )

        col_space, col_del = st.columns([4, 1])
        with col_del:
            if st.button("Eliminar", key=f"del_barbero_{bid_barber}", type="secondary", use_container_width=True):
                try:
                    safe_execute(
                        "DELETE FROM usuarios WHERE id = %s AND barberia_id = %s AND UPPER(TRIM(rol)) = 'BARBERO'",
                        (int(bid_barber), int(barberia_id)),
                    )
                    render_alert(
                        f"Barbero '{bname}' eliminado del equipo.",
                        alert_type="success",
                        title="Equipo actualizado",
                    )
                    st.rerun()
                except Exception:
                    logger.exception("Error eliminando barbero %s", bid_barber)
                    render_alert("Error al eliminar el barbero.", alert_type="error", title="Accion no completada")


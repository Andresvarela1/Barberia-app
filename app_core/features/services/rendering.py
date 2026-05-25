import streamlit as st

from app_core.db import safe_fetch_all
from app_core.services.servicios_service import (
    actualizar_servicio,
    crear_servicio,
    eliminar_servicio,
)
from design_system import (
    render_alert,
    render_divider,
    render_panel_empty_state,
    render_panel_header,
    render_subsection_title,
)

def render_services_section(
    *,
    barberia_id,
    db_ok,
    meta,
    no_context_message,
    no_db_message="Gestión de servicios no disponible sin base de datos",
):
    render_panel_header(
        "Servicios",
        "Crea, edita y elimina los servicios que ofrece tu barbería.",
        eyebrow="Catálogo",
        meta=meta,
    )

    if not db_ok:
        render_alert(no_db_message, alert_type="info", title="Modo demo")
        return

    if not barberia_id:
        render_alert(no_context_message, alert_type="info", title="Contexto requerido")
        return

    servicios_actuales = safe_fetch_all(
        "SELECT id, nombre, duracion_minutos, precio, descripcion, icono FROM servicios WHERE barberia_id = %s ORDER BY id ASC",
        (barberia_id,),
    )

    render_subsection_title("Agregar servicio")
    render_alert(
        "Los cambios del catálogo impactan de inmediato en el flujo de reservas.",
        alert_type="info",
        title="Catálogo activo",
    )

    with st.form("form_crear_servicio", clear_on_submit=True):
        col_n, col_d, col_p = st.columns([3, 2, 2])

        with col_n:
            nuevo_nombre = st.text_input("Nombre del servicio", max_chars=80)

        with col_d:
            nueva_duracion = st.number_input("Duración (min)", min_value=5, max_value=480, value=30, step=5)

        with col_p:
            nuevo_precio = st.number_input("Precio ($)", min_value=0, max_value=999999, value=0, step=100)

        nueva_descripcion = st.text_input("Descripción (opcional)", max_chars=200)
        nuevo_icono = st.text_input("Icono / etiqueta (opcional)", value="Servicio", max_chars=40)
        guardar = st.form_submit_button("Agregar servicio", use_container_width=True, type="primary")

    if guardar:
        if not nuevo_nombre or not nuevo_nombre.strip():
            render_alert("El nombre del servicio es obligatorio.", alert_type="error", title="Revisa los datos")
        else:
            ok = crear_servicio(
                barberia_id,
                nuevo_nombre,
                nueva_duracion,
                nuevo_precio,
                nueva_descripcion or "",
                nuevo_icono or "Servicio",
            )
            if ok:
                render_alert(
                    f"Servicio '{nuevo_nombre}' creado y disponible para reservas.",
                    alert_type="success",
                    title="Catálogo actualizado",
                )
                st.rerun()
            else:
                render_alert(
                    "Error al crear el servicio. Verifica que el nombre no este duplicado.",
                    alert_type="error",
                    title="Accion no completada",
                )

    render_divider()
    render_subsection_title("Servicios registrados")

    if not servicios_actuales:
        render_panel_empty_state(
            "Sin servicios aún",
            "Agrega un servicio con el formulario de arriba y aparecera aqui y en el flujo de reservas.",
        )
        return

    for row in servicios_actuales:
        sid, snombre, sduracion, sprecio, sdesc, sicono = row

        with st.expander(f"{sicono or 'Servicio'} — {snombre} | {sduracion} min | ${sprecio}", expanded=False):
            with st.form(f"form_editar_{sid}", clear_on_submit=False):
                col_en, col_ed, col_ep = st.columns([3, 2, 2])

                with col_en:
                    edit_nombre = st.text_input("Nombre", value=snombre, max_chars=80, key=f"en_{sid}")

                with col_ed:
                    edit_duracion = st.number_input(
                        "Duración (min)",
                        min_value=5,
                        max_value=480,
                        value=int(sduracion or 30),
                        step=5,
                        key=f"ed_{sid}",
                    )

                with col_ep:
                    edit_precio = st.number_input(
                        "Precio ($)",
                        min_value=0,
                        max_value=999999,
                        value=int(sprecio or 0),
                        step=100,
                        key=f"ep_{sid}",
                    )

                edit_desc = st.text_input("Descripción", value=sdesc or "", max_chars=200, key=f"edesc_{sid}")
                edit_icono = st.text_input("Icono / etiqueta", value=sicono or "Servicio", max_chars=40, key=f"eico_{sid}")

                col_save, col_del = st.columns(2)
                with col_save:
                    update_btn = st.form_submit_button("Guardar cambios", use_container_width=True, type="primary")
                with col_del:
                    delete_btn = st.form_submit_button("Eliminar servicio", use_container_width=True, type="secondary")

            if update_btn:
                if not edit_nombre or not edit_nombre.strip():
                    render_alert("El nombre no puede estar vacío.", alert_type="error", title="Revisa los datos")
                else:
                    ok = actualizar_servicio(
                        sid,
                        barberia_id,
                        edit_nombre,
                        edit_duracion,
                        edit_precio,
                        edit_desc or "",
                        edit_icono or "Servicio",
                    )
                    if ok:
                        render_alert("Servicio actualizado correctamente.", alert_type="success", title="Catálogo actualizado")
                        st.rerun()
                    else:
                        render_alert("Error al actualizar el servicio.", alert_type="error", title="Accion no completada")

            if delete_btn:
                ok = eliminar_servicio(sid, barberia_id)
                if ok:
                    render_alert(
                        f"Servicio '{snombre}' eliminado del catálogo.",
                        alert_type="success",
                        title="Catálogo actualizado",
                    )
                    st.rerun()
                else:
                    render_alert("Error al eliminar el servicio.", alert_type="error", title="Accion no completada")


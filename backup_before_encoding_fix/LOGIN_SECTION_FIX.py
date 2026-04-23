try:
    # Initialize session state
    if "user" not in st.session_state:
        st.session_state.user = None
    if "rol" not in st.session_state:
        st.session_state.rol = "CLIENTE"
    if "barberia_id" not in st.session_state:
        st.session_state.barberia_id = default_barberia_id
    if "barberia_context_id" not in st.session_state:
        st.session_state.barberia_context_id = default_barberia_id
    if "super_admin_all_barberias" not in st.session_state:
        st.session_state.super_admin_all_barberias = False
    if "reserva_seleccionada_id" not in st.session_state:
        st.session_state.reserva_seleccionada_id = None
    if "mostrar_detalles_reserva" not in st.session_state:
        st.session_state.mostrar_detalles_reserva = False

    st.session_state["db_available"] = is_db_available()
    db_ok = st.session_state["db_available"]
    render_modo_sin_db_banner()

    st.write("🔵 APP START")

    # ===== LOGIN SCREEN =====
    if not st.session_state.user:
        st.set_page_config(layout="wide")
        col_center = st.columns([1, 2, 1])
        with col_center[1]:
            st.markdown("# 💈 Barbería Leveling")
            st.markdown("**Tu plataforma de reservas profesional**")
            st.markdown("---")

            if not db_ok:
                st.warning(
                    "⚠️ Inicio de sesión y registro están desactivados: no hay base de datos (modo demo)."
                )

            opcion = st.radio("Selecciona una opción", [
                "🔑 Iniciar sesión",
                "✨ Registrar barbería",
            ], key="login_option")

            if opcion == "🔑 Iniciar sesión":
                st.markdown("### Accede a tu cuenta")
                with st.form("login_form"):
                    usuario = st.text_input("👤 Usuario", placeholder="Tu usuario")
                    password = st.text_input("🔐 Contraseña", type="password", placeholder="Tu contraseña")
                    entrar = st.form_submit_button("✅ Entrar", use_container_width=True, disabled=not db_ok)

                if entrar:
                    try:
                        with st.spinner("🔍 Verificando credenciales..."):
                            user = login(usuario, password)
                            if user:
                                # Store session state before rerun
                                st.session_state.user = user
                                # Normalize and store role immediately
                                raw_rol = user[3] if len(user) > 3 else None
                                st.session_state.rol = normalizar_rol(raw_rol)
                                nr_login = st.session_state.rol
                                st.write("🟢 LOGIN OK")
                                if nr_login == "SUPER_ADMIN":
                                    st.session_state.barberia_id = None
                                    with st.spinner("⏳ Cargando barberías..."):
                                        fb = fetch_one("SELECT id FROM barberias ORDER BY id LIMIT 1")
                                    st.session_state.barberia_context_id = fb[0] if fb else None
                                    st.session_state.super_admin_all_barberias = False
                                else:
                                    bid_u = user[5] if len(user) > 5 else None
                                    st.session_state.barberia_id = bid_u or default_barberia_id
                                    st.session_state.barberia_context_id = st.session_state.barberia_id
                                st.success("✅ ¡Bienvenido!")
                                st.rerun()
                            else:
                                st.error("❌ Datos incorrectos. Intenta nuevamente.")
                    except Exception as e:
                        logger.exception("Error en login")
                        st.error(f"Error en login: {str(e)}")

        # CRITICAL: Stop execution here ONLY when NOT logged in
        st.stop()

    # ===== MAIN APP (Only runs if logged in) =====
    st.write("🟡 MAIN APP STARTING")
    
    user = st.session_state.get("user")
    usuario = user[1] if user and len(user) > 1 else None
    # Always use normalized role from session state
    nr = st.session_state.get("rol", "CLIENTE")
    if not nr:
        st.session_state.rol = "CLIENTE"
        nr = "CLIENTE"

    barberia_id = st.session_state.get("barberia_id")
    bid_ctx = effective_barberia_id()

    if not db_ok:
        st.warning(
            "La base de datos no está disponible. Estás en modo demo: la interfaz se muestra, "
            "pero no se pueden crear ni modificar reservas ni consultar datos en vivo."
        )

    # ===== SIDEBAR =====
    with st.sidebar:
        st.markdown("## 💈 Barbería Leveling")
        st.markdown(f"**{usuario or 'Invitado'}**")
        st.caption(f"Rol: {nr.replace('_', ' ')}")

        barberia_name = "Principal"
        if barberia_id:
            if "barberia_name" not in st.session_state or st.session_state.get("cached_barberia_id") != barberia_id:
                with st.spinner("⏳ Cargando barbería..."):
                    b_name_row = fetch_one("SELECT nombre FROM barberias WHERE id = %s", (barberia_id,))
                st.session_state.barberia_name = b_name_row[0] if b_name_row else "Principal"
                st.session_state.cached_barberia_id = barberia_id
            barberia_name = st.session_state.barberia_name
        st.markdown(f"**Barbería:** {barberia_name}")
        st.markdown("---")

        if nr == "SUPER_ADMIN":
            st.markdown("### 🏢 Contexto")
            try:
                if "barberias_list" not in st.session_state:
                    with st.spinner("⏳ Cargando barberías..."):
                        b_list = fetch_all("SELECT id, nombre FROM barberias ORDER BY nombre") or []
                    st.session_state.barberias_list = b_list
                else:
                    b_list = st.session_state.barberias_list
                
                if b_list and len(b_list) > 0:
                    etiquetas = {f"{r[1]}": r[0] for r in b_list}
                    claves = list(etiquetas.keys())
                    
                    # Ensure valid index
                    idx = 0
                    if st.session_state.barberia_context_id is not None:
                        barberia_ids = list(etiquetas.values())
                        if st.session_state.barberia_context_id in barberia_ids:
                            idx = barberia_ids.index(st.session_state.barberia_context_id)
                        else:
                            idx = 0 if len(barberia_ids) > 0 else 0
                    
                    # Ensure index is within bounds
                    idx = min(idx, len(claves) - 1) if claves else 0
                    
                    if len(claves) > 0:
                        sel_lab = st.selectbox("Barbería activa", claves, index=idx, key="super_sel_barb")
                        st.session_state.barberia_context_id = etiquetas[sel_lab]
                    else:
                        st.warning("No hay barberías disponibles")
                else:
                    st.warning("No hay barberías registradas en el sistema")
                    st.session_state.barberia_context_id = None
            except Exception as e:
                logger.exception("Error loading barberia context for SUPER_ADMIN")
                st.error(f"Error cargando contexto de barbería: {str(e)}")
                st.session_state.barberia_context_id = None
            
            try:
                st.session_state.super_admin_all_barberias = st.checkbox(
                    "Ver todas las barberías",
                    value=st.session_state.get("super_admin_all_barberias", False),
                    key="chk_super_all",
                )
            except Exception as e:
                logger.exception("Error in SUPER_ADMIN checkbox")
                st.session_state.super_admin_all_barberias = False
            
            st.markdown("---")

        st.markdown("### 🗺️ Navegación")
        nav_opts = ["Dashboard", "Agenda", "Barberos", "Configuración"]
        if nr == "CLIENTE":
            nav_opts = ["Dashboard", "Agenda"]
        seccion = st.radio("", nav_opts, key=f"nav_main_{nr}", label_visibility="collapsed")

        st.markdown("---")
        if st.button("🚪 Cerrar sesión", use_container_width=True, type="secondary"):
            st.session_state.user = None
            st.session_state.barberia_id = None
            st.session_state.barberia_context_id = None
            st.rerun()

    def _panel_ingresos(bid):
        if not db_ok or not bid:
            st.info("Métricas de ingresos no disponibles sin base de datos.")
            return
        total_row = fetch_one(
            "SELECT SUM(precio) FROM reservas WHERE barberia_id = %s",
            (bid,),
        )
        total = total_row[0] if total_row is not None else 0
        if total is None:
            total = 0
        st.metric("Total generado", f"${total if total else 0}")

    try:
        eventos = obtener_reservas()
    except Exception as e:
        logger.exception("Error fetching reservas")
        eventos = []

    # ================= CLIENTE =================
    if nr == "CLIENTE":
        if not barberia_id:
            st.warning("No hay barberia asociada a la sesión.")
            st.stop()

        if seccion == "Dashboard":
            st.markdown("## 📊 Mi Panel")
            
            if not db_ok:
                st.info("📊 Métricas no disponibles sin base de datos.")
            else:
                with st.spinner("⏳ Cargando métricas..."):
                    total_reservas, hoy_reservas, _ = calcular_metricas_cliente(barberia_id, usuario)
                    num_barberos_cached = len(listar_usuarios_barberos(barberia_id))
                render_dashboard_cards(4, [
                    {"label": "📅 Total Reservas", "value": total_reservas},
                    {"label": "🎯 Reservas Hoy", "value": hoy_reservas},
                    {"label": "💰 Ingresos", "value": "$0"},
                    {"label": "👥 Barberos", "value": num_barberos_cached},
                ])
                st.markdown("---")
                st.markdown("### 💡 Información Útil")
                col_tip1, col_tip2 = st.columns(2, gap="large")
                with col_tip1:
                    st.success("✨ Obtén descuento cada 5 cortes")
                with col_tip2:
                    st.info("⏰ Cancela con 1 hora de anticipación")

        if seccion == "Agenda":
            st.markdown("## 📅 Mi Agenda")

            tab_calendario, tab_crear, tab_lista = st.tabs([
                "📅 Calendario",
                "✨ Nueva Reserva",
                "📋 Listado"
            ])

            # TAB: CALENDARIO
            with tab_calendario:
                if db_ok:
                    with st.spinner("⏳ Cargando tu calendario..."):
                        mis_reservas_raw = listar_reservas_filtradas(barberia_id, "CLIENTE", usuario)
                        # Convertir a formato para calendario
                        mis_reservas_dict = []
                        for r in mis_reservas_raw:
                            inicio = r[7] if len(r) > 7 else None
                            fin = inicio + timedelta(hours=1) if inicio else None
                            if inicio and fin:
                                mis_reservas_dict.append((r[0], r[5] or r[6], r[1], r[2], r[4], inicio, fin))
                        
                        eventos_cliente = construir_eventos_calendario(mis_reservas_dict)
                    
                    if eventos_cliente:
                        render_agenda_interactiva(eventos_cliente, read_only=True)
                    else:
                        st.info("📭 No tienes reservas aún. ¡Crea una!")
                else:
                    st.warning("Calendario no disponible sin base de datos.")

            # TAB: CREAR NUEVA
            with tab_crear:
                with st.container(border=True):
                    st.markdown("### ✨ Nueva Reserva")
                    if not db_ok:
                        st.warning("No hay base de datos: no puedes crear reservas en modo demo.")
                    else:
                        with st.spinner("⏳ Cargando barberos disponibles..."):
                            barber_opts = [x[0] for x in listar_usuarios_barberos(barberia_id)] or list(barberos.keys())
                        with st.form("form_reserva_cliente"):
                            col1, col2 = st.columns(2)
                            with col1:
                                barbero_sel = st.selectbox("💇 Barbero", barber_opts, key="cliente_barbero_sel")
                            with col2:
                                servicio_sel = st.selectbox("✂️ Servicio", list(servicios.keys()), key="cliente_servicio_sel")
                            
                            col3, col4 = st.columns(2)
                            with col3:
                                fecha_sel = st.date_input("📅 Fecha", key="cliente_fecha_sel")
                            with col4:
                                hora_sel = st.time_input("🕐 Hora", value=datetime.strptime("10:00", "%H:%M").time(), key="cliente_hora_sel")
                            
                            st.caption(f"👤 Cliente: **{usuario}**")
                            enviar = st.form_submit_button("✅ Reservar", use_container_width=True)

                        if enviar:
                            with st.spinner("⏳ Procesando reserva..."):
                                duracion = servicios[servicio_sel]["duracion"]
                                precio = servicios[servicio_sel]["precio"]
                                ok = insertar_reserva_con_fecha_hora(
                                    barberia_id,
                                    usuario,
                                    barbero_sel,
                                    servicio_sel,
                                    fecha_sel,
                                    hora_sel,
                                    precio,
                                    duracion,
                                )
                                if ok:
                                    procesar_beneficio_fidelizacion(usuario, barberia_id)
                                    inicio_msg = datetime.combine(fecha_sel, hora_sel)
                                    telefono_cliente = user[4] if len(user) > 4 else obtener_telefono_usuario(usuario)
                                    if telefono_cliente:
                                        mensaje = construir_mensaje_reserva(
                                            usuario, inicio_msg, barbero_sel, servicio_sel
                                        )
                                        try:
                                            enviar_whatsapp_twilio(telefono_cliente, mensaje)
                                        except Exception as exc:
                                            logger.exception("Error al ejecutar el envio de WhatsApp: %s", exc)
                                    st.success("✅ Reserva creada exitosamente")
                                    st.rerun()

            # TAB: LISTADO
            with tab_lista:
                st.markdown("### 📋 Tus Reservas")
                if not db_ok:
                    st.info("Lista de reservas no disponible sin base de datos.")
                else:
                    with st.spinner("Cargando datos..."):
                        mis_reservas = listar_reservas_filtradas(barberia_id, "CLIENTE", usuario)
                    if mis_reservas:
                        mostrar_reservas_dataframe(mis_reservas)
                        ui_eliminar_reserva_lista(mis_reservas, "cliente")
                    else:
                        st.info("📭 Aún no tienes reservas. ¡Crea una!")

    # ================= BARBERO =================
    elif nr == "BARBERO":
        if not barberia_id:
            st.warning("No hay barberia asociada a la sesión.")
            st.stop()

        if seccion == "Dashboard":
            st.markdown("## 📊 Mi Panel · Barbero")
            
            if not db_ok:
                st.info("📊 Métricas no disponibles sin base de datos.")
            else:
                with st.spinner("⏳ Cargando métricas..."):
                    total_reservas, hoy_reservas, total_ingresos = calcular_metricas_barbero(barberia_id, usuario)
                
                render_dashboard_cards(3, [
                    {"label": "✂️ Total Cortes", "value": total_reservas},
                    {"label": "🎯 Hoy", "value": hoy_reservas},
                    {"label": "💰 Ingresos", "value": f"${total_ingresos}"},
                ])
                
                st.markdown("---")
                with st.spinner("⏳ Cargando próximas citas..."):
                    reservas_barbero = listar_reservas_filtradas(barberia_id, "BARBERO", usuario)
                    hoy = datetime.now().date()
                    hoy_reservas_list = [r for r in reservas_barbero if r[3] == hoy]
                
                if hoy_reservas_list:
                    st.markdown("### 📌 Próximas Citas (Hoy)")
                    for r in hoy_reservas_list[:5]:
                        st.caption(f"🕐 {r[4]} - {r[5] or r[6]} ({r[2]})")

        if seccion == "Agenda":
            st.markdown("## 📅 Mi Agenda")
            
            tab_cal, tab_crear, tab_lista = st.tabs([
                "📆 Calendario",
                "➕ Crear/Editar",
                "📋 Listado"
            ])
            
            # TAB: CALENDARIO
            with tab_cal:
                if db_ok:
                    with st.spinner("Cargando datos..."):
                        eventos_barbero = obtener_reservas(usuario)
                    render_agenda_interactiva(eventos_barbero, usuario, read_only=False)
                else:
                    st.warning("Calendario no disponible sin base de datos (modo demo).")
            
            # TAB: CREAR/EDITAR
            with tab_crear:
                render_gestion_agenda(usuario)
            
            # TAB: LISTADO
            with tab_lista:
                st.markdown("### 📋 Mis Reservas")
                if not db_ok:
                    st.info("Tabla no disponible sin base de datos.")
                else:
                    with st.spinner("⏳ Cargando tus reservas..."):
                        rows_bar = listar_reservas_filtradas(barberia_id, "BARBERO", usuario)
                    if rows_bar:
                        mostrar_reservas_dataframe(rows_bar)
                        ui_marcar_pagado_reservas(rows_bar, "barbero_panel")
                        ui_eliminar_reserva_lista(rows_bar, "barbero_panel")
                    else:
                        st.info("📭 No hay reservas")

        if seccion == "Barberos":
            st.markdown("## 👥 Equipo")
            st.info("👨‍💼 Solo el administrador de la barbería gestiona el equipo de barberos.")

        if seccion == "Configuración":
            st.markdown("## ⚙️ Configuración")
            st.info("✨ Preferencias y ajustes próximamente.")

    # ================= ADMIN =================
    elif nr == "ADMIN":
        if not barberia_id:
            st.warning("No hay barberia asociada a la sesión.")
            st.stop()

        if seccion == "Dashboard":
            st.markdown("## 📊 Panel Administrativo")
            
            if not db_ok:
                st.info("📊 Métricas no disponibles sin base de datos.")
            else:
                with st.spinner("⏳ Cargando métricas..."):
                    total_reservas, hoy_reservas, total_ingresos, num_barberos = calcular_metricas_admin(barberia_id)
                
                render_dashboard_cards(4, [
                    {"label": "📅 Total Reservas", "value": total_reservas},
                    {"label": "🎯 Hoy", "value": hoy_reservas},
                    {"label": "💰 Ingresos (Pagadas)", "value": f"${total_ingresos}"},
                    {"label": "👥 Barberos", "value": num_barberos},
                ])
                
                st.markdown("---")
                with st.spinner("⏳ Cargando próximas citas..."):
                    todas_reservas = fetch_all(
                        """
                        SELECT id, barbero, servicio, fecha, hora, cliente, nombre, inicio, precio, estado, pagado, monto
                        FROM reservas
                        WHERE barberia_id = %s
                        ORDER BY inicio DESC
                        """,
                        (barberia_id,),
                    ) or []
                    hoy = datetime.now().date()
                    hoy_reservas_list = [r for r in todas_reservas if r[3] == hoy]
                
                if hoy_reservas_list:
                    st.markdown("### 📌 Próximas Citas (Hoy)")
                    for r in hoy_reservas_list[:5]:
                        st.caption(f"🕐 {r[4]} - {r[5] or r[6]} con {r[1]} ({r[2]})")

        if seccion == "Agenda":
            st.markdown("## 📅 Agenda")
            
            tab_cal, tab_crear, tab_lista, tab_ingresos = st.tabs([
                "📆 Calendario",
                "➕ Crear/Editar",
                "📋 Reservas",
                "💰 Ingresos"
            ])
            
            # TAB: CALENDARIO
            with tab_cal:
                if db_ok:
                    with st.spinner("⏳ Cargando calendario..."):
                        render_agenda_interactiva(eventos, read_only=not db_ok)
                else:
                    st.warning("Calendario no disponible sin base de datos (modo demo).")
            
            # TAB: CREAR/EDITAR
            with tab_crear:
                render_gestion_agenda()
            
            # TAB: RESERVAS
            with tab_lista:
                st.markdown("### 📋 Reservas")
                if not db_ok:
                    st.info("Tabla no disponible sin base de datos.")
                else:
                    filtro_adm = st.selectbox(
                        "Filtrar por barbero",
                        opciones_filtro_barberos_ui(barberia_id),
                        key="tabla_admin_filtro",
                    )
                    with st.spinner("Cargando datos..."):
                        rows_adm = listar_reservas_filtradas(
                            barberia_id, "ADMIN", usuario, filtro_barbero=filtro_adm
                        )
                    if rows_adm:
                        mostrar_reservas_dataframe(rows_adm)
                        ui_marcar_pagado_reservas(rows_adm, "admin_panel")
                        ui_eliminar_reserva_lista(rows_adm, "admin_panel")
                    else:
                        st.info("📭 No hay reservas")
            
            # TAB: INGRESOS
            with tab_ingresos:
                st.markdown("### 💰 Ingresos")
                if db_ok:
                    with st.spinner("Cargando datos..."):
                        total_row = fetch_one(
                            "SELECT SUM(monto) FROM reservas WHERE barberia_id = %s AND pagado = TRUE",
                            (barberia_id,),
                        )
                        total = total_row[0] if total_row and total_row[0] else 0
                    st.metric("💵 Ingresos Totales (Pagado)", f"${total}")
                    
                    st.markdown("---")
                    st.markdown("#### 📊 Desglose por Barbero")
                    with st.spinner("⏳ Cargando desglose..."):
                        barberos_list = listar_usuarios_barberos(barberia_id)
                        for barbero_name, _ in barberos_list:
                            barbero_ingresos = fetch_one(
                                "SELECT SUM(monto) FROM reservas WHERE barberia_id = %s AND barbero = %s AND pagado = TRUE",
                                (barberia_id, barbero_name),
                            )
                            ingreso = barbero_ingresos[0] if barbero_ingresos and barbero_ingresos[0] else 0
                            st.caption(f"💇 {barbero_name}: ${ingreso}")

        if seccion == "Barberos":
            st.markdown("## 👥 Gestión de Barberos")
            
            with st.container(border=True):
                st.markdown("### ➕ Nuevo Barbero")
                with st.form("crear_barbero_admin"):
                    col1, col2 = st.columns(2)
                    with col1:
                        nu = st.text_input("👤 Usuario", placeholder="Ej: Andrea")
                    with col2:
                        np = st.text_input("🔐 Contraseña", type="password")
                    if st.form_submit_button("✅ Crear Barbero", use_container_width=True):
                        with st.spinner("⏳ Creando barbero..."):
                            if registrar(nu, np, "BARBERO", barberia_id=barberia_id):
                                st.success("✅ Barbero creado exitosamente")
                                st.rerun()
            
            st.markdown("---")
            st.markdown("### 📋 Barberos Registrados")
            with st.spinner("⏳ Cargando barberos..."):
                barberos_data = listar_usuarios_barberos(barberia_id)
            if barberos_data:
                st.dataframe(
                    [{"👤 Usuario": r[0], "👥 Rol": r[1]} for r in barberos_data],
                    use_container_width=True,
                    hide_index=True,
                )
            else:
                st.info("📭 No hay barberos registrados aún")

        if seccion == "Configuración":
            st.markdown("## ⚙️ Configuración")
            st.info("✨ Datos de la barbería y preferencias próximamente.")

    # ================= SUPER_ADMIN =================
    elif nr == "SUPER_ADMIN":
        if seccion == "Dashboard":
            st.markdown("## 📊 Panel Global (Super Admin)")
            
            if not db_ok:
                st.info("📊 Métricas no disponibles sin base de datos.")
            else:
                with st.spinner("⏳ Cargando métricas globales..."):
                    num_barberias, num_usuarios, num_reservas, total_ingresos, hoy_count = calcular_metricas_super_admin(bid_ctx)
                
                render_dashboard_cards(5, [
                    {"label": "🏢 Barberías", "value": num_barberias},
                    {"label": "👥 Usuarios", "value": num_usuarios},
                    {"label": "📅 Total Reservas", "value": num_reservas},
                    {"label": "🎯 Hoy", "value": hoy_count},
                    {"label": "💰 Ingresos Totales", "value": f"${total_ingresos}"},
                ])

        if seccion == "Agenda":
            st.markdown("## 📅 Agenda Global")
            
            tab_cal, tab_crear, tab_lista, tab_ingresos = st.tabs([
                "📆 Calendario",
                "➕ Crear/Editar",
                "📋 Reservas",
                "💰 Ingresos"
            ])
            
            # TAB: CALENDARIO
            with tab_cal:
                if db_ok:
                    with st.spinner("⏳ Cargando calendario..."):
                        render_agenda_interactiva(eventos, read_only=not db_ok)
                else:
                    st.warning("Calendario no disponible sin base de datos (modo demo).")
            
            # TAB: CREAR/EDITAR
            with tab_crear:
                render_gestion_agenda()

            # TAB: RESERVAS
            with tab_lista:
                st.markdown("### 📋 Reservas")
                if not db_ok:
                    st.info("Tabla no disponible sin base de datos.")
                else:
                    filtro_su = st.selectbox(
                        "Filtrar por barbero",
                        opciones_filtro_barberos_ui(bid_ctx) if bid_ctx else ["Todos"] + list(barberos.keys()),
                        key="tabla_super_filtro",
                    )
                    with st.spinner("⏳ Cargando reservas..."):
                        rows_su = listar_reservas_filtradas(
                            bid_ctx, "SUPER_ADMIN", usuario, filtro_barbero=filtro_su
                        )
                    if rows_su:
                        mostrar_reservas_dataframe(rows_su)
                        ui_marcar_pagado_reservas(rows_su, "super_panel")
                        ui_eliminar_reserva_lista(rows_su, "super_panel")
                    else:
                        st.info("📭 No hay reservas")

            # TAB: INGRESOS
            with tab_ingresos:
                st.markdown("### 💰 Ingresos (Barbería Activa)")
                if db_ok and bid_ctx:
                    with st.spinner("⏳ Cargando datos de ingresos..."):
                        total_row = fetch_one(
                            "SELECT SUM(monto) FROM reservas WHERE barberia_id = %s AND pagado = TRUE",
                            (bid_ctx,),
                        )
                        total = total_row[0] if total_row and total_row[0] else 0
                    st.metric("💵 Ingresos Totales (Pagado)", f"${total}")
                    
                    st.markdown("---")
                    st.markdown("#### 📊 Desglose por Barbero")
                    with st.spinner("⏳ Cargando desglose..."):
                        barberos_list = listar_usuarios_barberos(bid_ctx)
                        for barbero_name, _ in barberos_list:
                            barbero_ingresos = fetch_one(
                                "SELECT SUM(monto) FROM reservas WHERE barberia_id = %s AND barbero = %s AND pagado = TRUE",
                                (bid_ctx, barbero_name),
                            )
                            ingreso = barbero_ingresos[0] if barbero_ingresos and barbero_ingresos[0] else 0
                            st.caption(f"💇 {barbero_name}: ${ingreso}")
                else:
                    st.info("Selecciona una barbería para ver ingresos")

        if seccion == "Barberos":
            st.markdown("## 👥 Barberos (Contexto)")
            if bid_ctx:
                with st.spinner("⏳ Cargando barberos..."):
                    barberos_data = listar_usuarios_barberos(bid_ctx)
                if barberos_data:
                    st.dataframe(
                        [{"👤 Usuario": r[0], "👥 Rol": r[1]} for r in barberos_data],
                        use_container_width=True,
                        hide_index=True,
                    )
                else:
                    st.info("📭 No hay barberos registrados")
            else:
                st.info("🏢 Selecciona una barbería en la barra lateral.")

        if seccion == "Configuración":
            st.markdown("## ⚙️ Configuración Global")
            st.info("✨ Parámetros de plataforma próximamente.")

    else:
        st.error(f"Vista no disponible para el rol: {nr}")

except Exception as e:
    logger.exception("Unhandled exception in Streamlit app")
    st.error(f"Error en la aplicación: {str(e)}")
    # Uncomment for debugging:
    # st.write(f"❌ DEBUG: Exception caught in main try block: {str(e)}")
    # import traceback
    # st.write(traceback.format_exc())

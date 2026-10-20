/* Lightweight interface translations for the app's supported languages. */
(() => {
  const rows = [
    ["Growth workspace", "Espacio de crecimiento", "Espace de croissance", "ग्रोथ वर्कस्पेस"],
    ["Growth & Lead Intelligence Platform", "Plataforma de inteligencia de crecimiento y clientes potenciales", "Plateforme d'intelligence de croissance et de prospects", "ग्रोथ और लीड इंटेलिजेंस प्लेटफ़ॉर्म"],
    ["WORKSPACE", "ESPACIO DE TRABAJO", "ESPACE DE TRAVAIL", "कार्यस्थान"],
    ["TOOLS", "HERRAMIENTAS", "OUTILS", "उपकरण"],
    ["Overview", "Resumen", "Vue d'ensemble", "अवलोकन"],
    ["Dashboard", "Panel", "Tableau de bord", "डैशबोर्ड"],
    ["Upload dataset", "Subir conjunto de datos", "Importer un jeu de données", "डेटासेट अपलोड करें"],
    ["Data explorer", "Explorador de datos", "Explorateur de données", "डेटा एक्सप्लोरर"],
    ["Funnel analytics", "Análisis del embudo", "Analyse de l'entonnoir", "फ़नल विश्लेषण"],
    ["Lead segmentation", "Segmentación de clientes potenciales", "Segmentation des prospects", "लीड विभाजन"],
    ["Lead segments", "Segmentos de clientes potenciales", "Segments de prospects", "लीड सेगमेंट"],
    ["KPI analytics", "Análisis de KPI", "Analyse des KPI", "KPI विश्लेषण"],
    ["AI insights", "Información de IA", "Analyses IA", "AI अंतर्दृष्टि"],
    ["AI analyst", "Analista de IA", "Analyste IA", "AI विश्लेषक"],
    ["Ask AI analyst", "Preguntar al analista de IA", "Interroger l'analyste IA", "AI विश्लेषक से पूछें"],
    ["Experiments", "Experimentos", "Expériences", "प्रयोग"],
    ["Reports", "Informes", "Rapports", "रिपोर्ट"],
    ["Settings", "Configuración", "Paramètres", "सेटिंग्स"],
    ["Log out", "Cerrar sesión", "Se déconnecter", "लॉग आउट"],
    ["Live workspace", "Espacio de trabajo activo", "Espace de travail actif", "लाइव वर्कस्पेस"],
    ["Workspace", "Espacio de trabajo", "Espace de travail", "वर्कस्पेस"],
    ["Something went wrong", "Se produjo un error", "Une erreur s'est produite", "कुछ गलत हुआ"],
    ["YOUR NEXT GROWTH CHAPTER", "TU PRÓXIMA ETAPA DE CRECIMIENTO", "VOTRE PROCHAINE ÉTAPE DE CROISSANCE", "आपकी अगली विकास यात्रा"],
    ["Turn your data", "Convierte tus datos", "Transformez vos données", "अपने डेटा को बदलें"],
    ["into", "en", "en", "में"],
    ["momentum.", "impulso.", "dynamique.", "गति में।"],
    ["One clear view of your leads, performance, and what to do next. Make confident moves with the whole picture in focus.", "Una visión clara de tus clientes potenciales y resultados para decidir qué hacer. Avanza con confianza y una perspectiva completa.", "Une vue claire de vos prospects et de vos résultats pour savoir quoi faire ensuite. Décidez avec confiance grâce à une vision complète.", "अपने लीड और प्रदर्शन को स्पष्ट रूप से देखें और जानें कि आगे क्या करना है। पूरी तस्वीर के साथ आत्मविश्वास से निर्णय लें।"],
    ["See what’s working", "Descubre qué funciona", "Voyez ce qui fonctionne", "जानें क्या काम कर रहा है"],
    ["Get a sharper view of performance", "Obtén una visión más clara del rendimiento", "Obtenez une vision plus précise des performances", "प्रदर्शन की बेहतर समझ पाएँ"],
    ["Find your next opportunity", "Encuentra tu próxima oportunidad", "Trouvez votre prochaine opportunité", "अपना अगला अवसर खोजें"],
    ["Turn insights into action", "Convierte los hallazgos en acciones", "Transformez les analyses en actions", "जानकारियों को कार्रवाई में बदलें"],
    ["GROWTH PULSE", "IMPULSO DE CRECIMIENTO", "DYNAMIQUE DE CROISSANCE", "ग्रोथ पल्स"],
    ["YOUR WORKSPACE", "TU ESPACIO DE TRABAJO", "VOTRE ESPACE DE TRAVAIL", "आपका वर्कस्पेस"],
    ["Progress, at a glance", "Tu progreso de un vistazo", "Votre progression en un coup d'œil", "एक नज़र में प्रगति"],
    ["Your data. A clearer direction.", "Tus datos. Un rumbo más claro.", "Vos données. Une direction plus claire.", "आपका डेटा। एक स्पष्ट दिशा।"],
    ["From first signal", "Desde la primera señal", "Dès le premier signal", "पहले संकेत से"],
    ["To your next big move", "Hasta tu próximo gran paso", "Jusqu'à votre prochaine grande décision", "आपके अगले बड़े कदम तक"],
    ["BUILT FOR THE CURIOUS AND AMBITIOUS", "PARA PERSONAS CURIOSAS Y AMBICIOSAS", "CONÇU POUR LES CURIEUX ET LES AMBITIEUX", "जिज्ञासु और महत्वाकांक्षी लोगों के लिए"],
    ["Make every insight count.", "Aprovecha cada hallazgo.", "Donnez du sens à chaque analyse.", "हर जानकारी को उपयोगी बनाएँ।"],
    ["WELCOME BACK", "TE DAMOS LA BIENVENIDA", "BON RETOUR", "वापस स्वागत है"],
    ["Good to see you.", "Qué bueno verte.", "Ravi de vous revoir.", "आपसे मिलकर अच्छा लगा।"],
    ["Sign in to pick up where your next chapter begins.", "Inicia sesión para continuar tu próximo capítulo.", "Connectez-vous pour reprendre le fil de votre prochaine étape.", "अपनी अगली यात्रा जारी रखने के लिए साइन इन करें।"],
    ["Work email", "Correo electrónico de trabajo", "E-mail professionnel", "कार्य ईमेल"],
    ["Password", "Contraseña", "Mot de passe", "पासवर्ड"],
    ["Enter your password", "Introduce tu contraseña", "Saisissez votre mot de passe", "अपना पासवर्ड दर्ज करें"],
    ["Sign in", "Iniciar sesión", "Se connecter", "साइन इन"],
    ["New to Growth Intel?", "¿Eres nuevo en Growth Intel?", "Nouveau sur Growth Intel ?", "Growth Intel पर नए हैं?"],
    ["Create your workspace", "Crea tu espacio de trabajo", "Créer votre espace de travail", "अपना वर्कस्पेस बनाएँ"],
    ["Your workspace is private and secure", "Tu espacio de trabajo es privado y seguro", "Votre espace de travail est privé et sécurisé", "आपका वर्कस्पेस निजी और सुरक्षित है"],
    ["A clearer path to growth", "Un camino más claro hacia el crecimiento", "Une voie plus claire vers la croissance", "विकास का अधिक स्पष्ट रास्ता"],
    ["Start analyzing your growth data in minutes", "Empieza a analizar tus datos de crecimiento en minutos", "Analysez vos données de croissance en quelques minutes", "मिनटों में अपने विकास डेटा का विश्लेषण शुरू करें"],
    ["Organization name", "Nombre de la organización", "Nom de l'organisation", "संगठन का नाम"],
    ["Full name", "Nombre completo", "Nom complet", "पूरा नाम"],
    ["Email", "Correo electrónico", "E-mail", "ईमेल"],
    ["Create Account", "Crear cuenta", "Créer un compte", "खाता बनाएँ"],
    ["Already have an account?", "¿Ya tienes una cuenta?", "Vous avez déjà un compte ?", "क्या आपका खाता पहले से है?"],
    ["Analyzed dataset:", "Conjunto de datos analizado:", "Jeu de données analysé :", "विश्लेषित डेटासेट:"],
    ["No analyzed datasets are available yet.", "Aún no hay conjuntos de datos analizados.", "Aucun jeu de données analysé pour le moment.", "अभी कोई विश्लेषित डेटासेट उपलब्ध नहीं है।"],
    ["Continue dataset analysis", "Continuar el análisis del conjunto de datos", "Continuer l'analyse du jeu de données", "डेटासेट विश्लेषण जारी रखें"],
    ["Upload your first dataset", "Sube tu primer conjunto de datos", "Importer votre premier jeu de données", "अपना पहला डेटासेट अपलोड करें"],
    [" rows", " filas", " lignes", " पंक्तियाँ"],
    ["GROWTH OVERVIEW", "RESUMEN DE CRECIMIENTO", "VUE D'ENSEMBLE DE LA CROISSANCE", "ग्रोथ अवलोकन"],
    ["Know your numbers.", "Conoce tus cifras.", "Maîtrisez vos chiffres.", "अपने आँकड़े जानें।"],
    ["Grow with confidence.", "Crece con confianza.", "Développez-vous en toute confiance.", "आत्मविश्वास से आगे बढ़ें।"],
    ["Your latest performance, funnel health, and opportunities — all in one place.", "Tus resultados recientes, el estado del embudo y las oportunidades, todo en un solo lugar.", "Vos performances récentes, la santé de l'entonnoir et les opportunités, réunies au même endroit.", "आपका हालिया प्रदर्शन, फ़नल की स्थिति और अवसर—सब एक ही जगह।"],
    ["Add dataset", "Añadir conjunto de datos", "Ajouter un jeu de données", "डेटासेट जोड़ें"],
    ["No analyzed dataset selected", "No hay un conjunto de datos analizado seleccionado", "Aucun jeu de données analysé sélectionné", "कोई विश्लेषित डेटासेट चयनित नहीं है"],
    ["No dataset selected", "No hay un conjunto de datos seleccionado", "Aucun jeu de données sélectionné", "कोई डेटासेट चयनित नहीं है"],
    ["Upload and analyze a dataset first.", "Primero sube y analiza un conjunto de datos.", "Importez et analysez d'abord un jeu de données.", "पहले डेटासेट अपलोड करके विश्लेषण करें।"],
    ["Upload a CSV/XLSX file and run analysis to see your dashboard.", "Sube un archivo CSV/XLSX y ejecuta el análisis para ver tu panel.", "Importez un fichier CSV/XLSX et lancez l'analyse pour afficher votre tableau de bord.", "डैशबोर्ड देखने के लिए CSV/XLSX फ़ाइल अपलोड करके विश्लेषण चलाएँ।"],
    ["Performance at a glance", "Rendimiento de un vistazo", "Performances en un coup d'œil", "एक नज़र में प्रदर्शन"],
    ["A clear snapshot of your selected dataset", "Un resumen claro del conjunto de datos seleccionado", "Un aperçu clair du jeu de données sélectionné", "आपके चयनित डेटासेट का स्पष्ट सारांश"],
    ["Live data", "Datos en directo", "Données en direct", "लाइव डेटा"],
    ["Total Leads", "Clientes potenciales totales", "Total des prospects", "कुल लीड"],
    ["Overall Conversion", "Conversión general", "Conversion globale", "कुल रूपांतरण"],
    ["Revenue", "Ingresos", "Revenu", "राजस्व"],
    ["Activation Rate", "Tasa de activación", "Taux d'activation", "सक्रियण दर"],
    ["Trial → Payment", "Prueba → Pago", "Essai → Paiement", "ट्रायल → भुगतान"],
    ["Current dataset", "Conjunto de datos actual", "Jeu de données actuel", "वर्तमान डेटासेट"],
    ["CONVERSION", "CONVERSIÓN", "CONVERSION", "रूपांतरण"],
    ["Funnel performance", "Rendimiento del embudo", "Performances de l'entonnoir", "फ़नल प्रदर्शन"],
    ["AUDIENCE", "AUDIENCIA", "AUDIENCE", "ऑडियंस"],
    ["Segment mix", "Composición de segmentos", "Répartition des segments", "सेगमेंट मिश्रण"],
    ["Trends over time", "Tendencias a lo largo del tiempo", "Tendances dans le temps", "समय के साथ रुझान"],
    ["See where momentum is building", "Descubre dónde aumenta el impulso", "Repérez où la dynamique s'accélère", "जानें कि प्रगति कहाँ बढ़ रही है"],
    ["REVENUE", "INGRESOS", "REVENUS", "राजस्व"],
    ["Revenue trend", "Tendencia de ingresos", "Tendance des revenus", "राजस्व रुझान"],
    ["· latest 30 days", "· últimos 30 días", "· 30 derniers jours", "· पिछले 30 दिन"],
    ["ACQUISITION", "ADQUISICIÓN", "ACQUISITION", "अधिग्रहण"],
    ["Lead trend", "Tendencia de clientes potenciales", "Tendance des prospects", "लीड रुझान"],
    ["Signals & opportunities", "Señales y oportunidades", "Signaux et opportunités", "संकेत और अवसर"],
    ["Useful next steps from your latest data", "Próximos pasos útiles a partir de tus datos recientes", "Prochaines étapes utiles à partir de vos données récentes", "आपके हालिया डेटा से उपयोगी अगले कदम"],
    ["YOUR AI ANALYST", "TU ANALISTA DE IA", "VOTRE ANALYSTE IA", "आपका AI विश्लेषक"],
    ["Growth insights", "Información de crecimiento", "Analyses de croissance", "ग्रोथ अंतर्दृष्टि"],
    ["Generate AI insights", "Generar análisis de IA", "Générer des analyses IA", "AI अंतर्दृष्टि बनाएँ"],
    ["ANOMALY MONITOR", "MONITOR DE ANOMALÍAS", "SURVEILLANCE DES ANOMALIES", "विसंगति निगरानी"],
    ["Worth a closer look", "Merece una revisión", "À examiner de plus près", "ध्यान से देखने योग्य"],
    ["No anomalies detected in the last 90 days. ✅", "No se detectaron anomalías en los últimos 90 días. ✅", "Aucune anomalie détectée au cours des 90 derniers jours. ✅", "पिछले 90 दिनों में कोई विसंगति नहीं मिली। ✅"],
    ["Time-series needs date data.", "La serie temporal necesita fechas.", "La série chronologique nécessite des dates.", "समय-श्रृंखला के लिए दिनांक डेटा चाहिए।"],
    ["This dataset has no mapped signup or payment dates, so there are no real daily trends to plot. Map", "Este conjunto de datos no tiene fechas de registro o pago asignadas, por lo que no hay tendencias diarias reales que mostrar. Asigna", "Ce jeu de données ne comporte aucune date d'inscription ou de paiement associée : aucune tendance quotidienne réelle ne peut être affichée. Associez", "इस डेटासेट में साइन-अप या भुगतान की मैप की गई तारीखें नहीं हैं, इसलिए वास्तविक दैनिक रुझान नहीं दिख सकते। मैप करें"],
    ["for leads and", "para clientes potenciales y", "pour les prospects et", "लीड के लिए और"],
    ["for revenue during upload, or choose a dated dataset such as", "para los ingresos al subir el archivo, o elige un conjunto de datos con fechas como", "pour les revenus lors de l'importation, ou choisissez un jeu de données daté comme", "अपलोड के दौरान राजस्व के लिए, या दिनांक वाला डेटासेट चुनें जैसे"],
    ["No date data", "Sin datos de fecha", "Aucune donnée de date", "दिनांक डेटा नहीं"],
    ["No dated records available", "No hay registros con fecha", "Aucun enregistrement daté disponible", "दिनांक वाले रिकॉर्ड उपलब्ध नहीं हैं"],
    ["Map", "Asigna", "Associez", "मैप करें"],
    ["Not enough data yet", "Aún no hay suficientes datos", "Pas encore assez de données", "अभी पर्याप्त डेटा नहीं है"],
    ["Lead", "Cliente potencial", "Prospect", "लीड"],
    ["Signup", "Registro", "Inscription", "साइन-अप"],
    ["Trial", "Prueba", "Essai", "ट्रायल"],
    ["Trial started", "Prueba iniciada", "Essai commencé", "ट्रायल शुरू हुआ"],
    ["Activated", "Activado", "Activé", "सक्रिय"],
    ["Payment", "Pago", "Paiement", "भुगतान"],
    ["Paid", "Pagado", "Payé", "भुगतान किया"],
    ["Users", "Usuarios", "Utilisateurs", "उपयोगकर्ता"],
    ["LATEST 30 DAYS", "ÚLTIMOS 30 DÍAS", "30 DERNIERS JOURS", "पिछले 30 दिन"],
    ["vs prior 30 days", "frente a los 30 días anteriores", "par rapport aux 30 jours précédents", "पिछले 30 दिनों की तुलना में"],
    ["No previous-period comparison", "Sin comparación con el período anterior", "Aucune comparaison avec la période précédente", "पिछली अवधि से तुलना उपलब्ध नहीं"],
    ["Upload Dataset", "Subir conjunto de datos", "Importer un jeu de données", "डेटासेट अपलोड करें"],
    ["Upload a CSV or Excel file with lead/customer data. We'll auto-detect columns, flag data-quality issues, and let you confirm the mapping before analysis.", "Sube un archivo CSV o Excel con datos de clientes potenciales o clientes. Detectaremos las columnas, señalaremos problemas de calidad y podrás confirmar la asignación antes del análisis.", "Importez un fichier CSV ou Excel contenant des données de prospects ou de clients. Les colonnes seront détectées, les problèmes de qualité signalés et vous pourrez confirmer leur correspondance avant l'analyse.", "लीड/ग्राहक डेटा वाली CSV या Excel फ़ाइल अपलोड करें। हम कॉलम पहचानेंगे, डेटा गुणवत्ता की समस्याएँ बताएँगे और विश्लेषण से पहले मैपिंग की पुष्टि करने देंगे।"],
    ["Upload & Preview", "Subir y previsualizar", "Importer et prévisualiser", "अपलोड और पूर्वावलोकन"],
    ["Uploading…", "Subiendo…", "Importation…", "अपलोड हो रहा है…"],
    ["File uploaded. Review the column mapping below.", "Archivo subido. Revisa la asignación de columnas.", "Fichier importé. Vérifiez la correspondance des colonnes ci-dessous.", "फ़ाइल अपलोड हो गई। नीचे कॉलम मैपिंग देखें।"],
    ["Data Quality Preview", "Vista previa de calidad de datos", "Aperçu de la qualité des données", "डेटा गुणवत्ता पूर्वावलोकन"],
    ["Total Rows", "Filas totales", "Nombre total de lignes", "कुल पंक्तियाँ"],
    ["Columns", "Columnas", "Colonnes", "कॉलम"],
    ["Duplicate Rows", "Filas duplicadas", "Lignes en double", "डुप्लिकेट पंक्तियाँ"],
    ["Auto-mapped Columns", "Columnas asignadas automáticamente", "Colonnes associées automatiquement", "स्वतः मैप किए गए कॉलम"],
    ["Confirm Column Mapping", "Confirmar asignación de columnas", "Confirmer la correspondance des colonnes", "कॉलम मैपिंग की पुष्टि करें"],
    ["Source Column", "Columna de origen", "Colonne source", "स्रोत कॉलम"],
    ["Detected Type", "Tipo detectado", "Type détecté", "पहचाना गया प्रकार"],
    ["Missing %", "% faltante", "% manquant", "गुम %"],
    ["Maps To", "Se asigna a", "Correspond à", "इससे मैप करें"],
    ["(unmapped)", "(sin asignar)", "(non associé)", "(मैप नहीं किया)"],
    ["Confirm Mapping & Run Analysis", "Confirmar asignación y ejecutar análisis", "Confirmer la correspondance et lancer l'analyse", "मैपिंग की पुष्टि करें और विश्लेषण चलाएँ"],
    ["Running analysis…", "Ejecutando análisis…", "Analyse en cours…", "विश्लेषण चल रहा है…"],
    ["Analysis complete! Redirecting to dashboard…", "¡Análisis completado! Redirigiendo al panel…", "Analyse terminée ! Redirection vers le tableau de bord…", "विश्लेषण पूरा हुआ! डैशबोर्ड पर जा रहे हैं…"],
    ["Sample Rows", "Filas de ejemplo", "Lignes d'exemple", "नमूना पंक्तियाँ"],
    ["Analysis failed.", "El análisis falló.", "L'analyse a échoué.", "विश्लेषण विफल हुआ।"],
    ["Analysis is taking longer than expected. Check back in a moment.", "El análisis está tardando más de lo esperado. Vuelve a comprobarlo en un momento.", "L'analyse prend plus de temps que prévu. Réessayez dans un instant.", "विश्लेषण में अपेक्षा से अधिक समय लग रहा है। थोड़ी देर में फिर देखें।"],
    ["Search by name or email…", "Buscar por nombre o correo…", "Rechercher par nom ou e-mail…", "नाम या ईमेल से खोजें…"],
    [" rows total", " filas en total", " lignes au total", " कुल पंक्तियाँ"],
    ["No rows found", "No se encontraron filas", "Aucune ligne trouvée", "कोई पंक्ति नहीं मिली"],
    ["← Previous", "← Anterior", "← Précédent", "← पिछला"],
    ["Next →", "Siguiente →", "Suivant →", "अगला →"],
    ["Page", "Página", "Page", "पृष्ठ"],
    ["Yes", "Sí", "Oui", "हाँ"],
    ["No", "No", "Non", "नहीं"],
    ["CONVERSION JOURNEY", "RECORRIDO DE CONVERSIÓN", "PARCOURS DE CONVERSION", "रूपांतरण यात्रा"],
    ["Funnel", "Análisis del", "Analyse de l'", "फ़नल"],
    ["analytics.", "embudo.", "entonnoir.", "विश्लेषण।"],
    ["See how leads move from first touch to payment, and where they drop off.", "Descubre cómo avanzan los clientes potenciales desde el primer contacto hasta el pago y dónde abandonan.", "Suivez le parcours des prospects, du premier contact au paiement, et repérez les abandons.", "जानें कि लीड पहले संपर्क से भुगतान तक कैसे बढ़ते हैं और कहाँ रुकते हैं।"],
    ["Your conversion journey", "Tu recorrido de conversión", "Votre parcours de conversion", "आपकी रूपांतरण यात्रा"],
    ["records tracked through each stage", "registros seguidos en cada etapa", "enregistrements suivis à chaque étape", "रिकॉर्ड हर चरण में ट्रैक किए गए"],
    ["Your funnel is waiting for stage data", "Tu embudo espera datos de etapas", "Votre entonnoir attend des données d'étape", "आपका फ़नल चरण डेटा की प्रतीक्षा कर रहा है"],
    ["This dataset has records, but no signup, trial, activation, or payment dates. Map the relevant date columns to these fields during upload to see your conversion journey.", "Este conjunto de datos tiene registros, pero no fechas de registro, prueba, activación o pago. Asigna las columnas de fecha correspondientes al subir el archivo para ver el recorrido de conversión.", "Ce jeu de données contient des enregistrements, mais aucune date d'inscription, d'essai, d'activation ou de paiement. Associez les colonnes de dates correspondantes lors de l'importation pour afficher votre parcours de conversion.", "इस डेटासेट में रिकॉर्ड हैं, लेकिन साइन-अप, ट्रायल, सक्रियण या भुगतान की तारीखें नहीं हैं। रूपांतरण यात्रा देखने के लिए अपलोड करते समय संबंधित तारीख कॉलम मैप करें।"],
    ["Upload or map data", "Subir o asignar datos", "Importer ou associer des données", "डेटा अपलोड या मैप करें"],
    ["STAGE-BY-STAGE", "ETAPA POR ETAPA", "ÉTAPE PAR ÉTAPE", "चरण-दर-चरण"],
    ["Conversion funnel", "Embudo de conversión", "Entonnoir de conversion", "रूपांतरण फ़नल"],
    ["No conversion stages to plot yet", "Aún no hay etapas de conversión para mostrar", "Aucune étape de conversion à afficher pour le moment", "दिखाने के लिए अभी कोई रूपांतरण चरण नहीं"],
    ["Once signup or later-stage dates are mapped, your funnel will appear here.", "Cuando se asignen las fechas de registro o de etapas posteriores, el embudo aparecerá aquí.", "Une fois les dates d'inscription ou des étapes suivantes associées, votre entonnoir apparaîtra ici.", "साइन-अप या अगले चरणों की तारीखें मैप होने के बाद फ़नल यहाँ दिखाई देगा।"],
    ["Biggest drop-off:", "Mayor abandono:", "Abandon le plus important :", "सबसे अधिक गिरावट:"],
    ["Stage", "Etapa", "Étape", "चरण"],
    ["Users", "Usuarios", "Utilisateurs", "उपयोगकर्ता"],
    ["Conv. from Previous", "Conversión desde anterior", "Conv. depuis l'étape précédente", "पिछले चरण से रूपांतरण"],
    ["Drop-off", "Abandono", "Abandon", "गिरावट"],
    ["Conv. from Start", "Conversión desde el inicio", "Conv. depuis le début", "शुरुआत से रूपांतरण"],
    ["leads", "clientes potenciales", "prospects", "लीड"],
    ["Conversion", "Conversión", "Conversion", "रूपांतरण"],
    ["Total Revenue", "Ingresos totales", "Revenu total", "कुल राजस्व"],
    ["Avg Engagement", "Interacción media", "Engagement moyen", "औसत सहभागिता"],
    ["Top source:", "Fuente principal:", "Principale source :", "शीर्ष स्रोत:"],
    ["% of total", "% del total", "% du total", "कुल का %"],
    ["Source", "Fuente", "Source", "स्रोत"],
    ["Plan", "Plan", "Offre", "योजना"],
    ["Country", "País", "Pays", "देश"],
    ["e.g. google", "p. ej., google", "ex. google", "जैसे google"],
    ["e.g. Pro", "p. ej., Pro", "ex. Pro", "जैसे Pro"],
    ["Apply Filters", "Aplicar filtros", "Appliquer les filtres", "फ़िल्टर लागू करें"],
    ["Clear", "Borrar", "Effacer", "साफ़ करें"],
    ["Generate fresh AI-powered insights from the current analysis, or view the most recent ones.", "Genera nuevos análisis con IA a partir del análisis actual o consulta los más recientes.", "Générez de nouvelles analyses IA à partir de l'analyse actuelle ou consultez les plus récentes.", "मौजूदा विश्लेषण से नए AI अंतर्दृष्टि बनाएँ या हाल के परिणाम देखें।"],
    ["✨ Generate Insights", "✨ Generar análisis", "✨ Générer des analyses", "✨ अंतर्दृष्टि बनाएँ"],
    ["Thinking…", "Pensando…", "Réflexion…", "सोच रहा है…"],
    ["No insights yet", "Aún no hay análisis", "Aucune analyse pour le moment", "अभी कोई अंतर्दृष्टि नहीं"],
    ["Click 'Generate Insights' to get an AI-powered analysis of this dataset.", "Pulsa «Generar análisis» para obtener un análisis de este conjunto de datos con IA.", "Cliquez sur « Générer des analyses » pour obtenir une analyse IA de ce jeu de données.", "इस डेटासेट का AI विश्लेषण पाने के लिए 'अंतर्दृष्टि बनाएँ' पर क्लिक करें।"],
    ["LLM-generated", "Generado por LLM", "Généré par LLM", "LLM द्वारा जनरेट"],
    ["Rule-based (no LLM key configured)", "Basado en reglas (no hay clave LLM configurada)", "Basé sur des règles (aucune clé LLM configurée)", "नियम-आधारित (LLM कुंजी कॉन्फ़िगर नहीं है)"],
    ["Executive Summary", "Resumen ejecutivo", "Résumé exécutif", "कार्यकारी सारांश"],
    ["Key Findings", "Hallazgos clave", "Constats clés", "मुख्य निष्कर्ष"],
    ["Problems", "Problemas", "Problèmes", "समस्याएँ"],
    ["Opportunities", "Oportunidades", "Opportunités", "अवसर"],
    ["Recommended Actions", "Acciones recomendadas", "Actions recommandées", "अनुशंसित कार्रवाइयाँ"],
    ["Insufficient data to determine this.", "No hay datos suficientes para determinarlo.", "Données insuffisantes pour le déterminer.", "यह निर्धारित करने के लिए पर्याप्त डेटा नहीं है।"],
    ["🧪 Experiment Ideas", "🧪 Ideas de experimentos", "🧪 Idées d'expériences", "🧪 प्रयोग के विचार"],
    ["Hypothesis:", "Hipótesis:", "Hypothèse :", "परिकल्पना:"],
    ["Experiment:", "Experimento:", "Expérience :", "प्रयोग:"],
    ["Metric:", "Métrica:", "Indicateur :", "मेट्रिक:"],
    ["Expected:", "Esperado:", "Attendu :", "अपेक्षित:"],
    ["Add to Experiments", "Añadir a experimentos", "Ajouter aux expériences", "प्रयोगों में जोड़ें"],
    ["Added to Experiments.", "Añadido a experimentos.", "Ajouté aux expériences.", "प्रयोगों में जोड़ा गया।"],
    ["Which lead source performs best?", "¿Qué fuente de clientes potenciales funciona mejor?", "Quelle source de prospects est la plus performante ?", "कौन सा लीड स्रोत सबसे अच्छा प्रदर्शन करता है?"],
    ["Where is the biggest funnel drop-off?", "¿Dónde se produce el mayor abandono del embudo?", "Où se produit le plus grand abandon dans l'entonnoir ?", "फ़नल में सबसे अधिक गिरावट कहाँ है?"],
    ["Give me the top growth opportunities.", "Dame las principales oportunidades de crecimiento.", "Donnez-moi les principales opportunités de croissance.", "मुझे विकास के शीर्ष अवसर बताएँ।"],
    ["What should we test next?", "¿Qué deberíamos probar después?", "Que devrions-nous tester ensuite ?", "हमें आगे क्या परीक्षण करना चाहिए?"],
    ["Try asking:", "Prueba a preguntar:", "Essayez de demander :", "यह पूछकर देखें:"],
    ["Ask about your business data, e.g. 'Why did conversion decrease?'", "Pregunta sobre los datos de tu negocio, por ejemplo: «¿Por qué bajó la conversión?»", "Posez une question sur vos données, par exemple : « Pourquoi la conversion a-t-elle baissé ? »", "अपने व्यावसायिक डेटा के बारे में पूछें, जैसे 'रूपांतरण क्यों घटा?'"],
    ["Ask", "Preguntar", "Demander", "पूछें"],
    ["Rule-based", "Basado en reglas", "Basé sur des règles", "नियम-आधारित"],
    ["+ New Experiment", "+ Nuevo experimento", "+ Nouvelle expérience", "+ नया प्रयोग"],
    ["New", "Nuevo", "Nouveau", "नया"],
    ["Edit", "Editar", "Modifier", "संपादित करें"],
    ["Delete", "Eliminar", "Supprimer", "हटाएँ"],
    ["Delete this experiment?", "¿Eliminar este experimento?", "Supprimer cette expérience ?", "क्या यह प्रयोग हटाएँ?"],
    ["No experiments yet", "Aún no hay experimentos", "Aucune expérience pour le moment", "अभी कोई प्रयोग नहीं"],
    ["Create one manually, or generate ideas from AI Insights.", "Crea uno manualmente o genera ideas desde los análisis de IA.", "Créez-en une manuellement ou générez des idées à partir des analyses IA.", "एक मैन्युअल रूप से बनाएँ या AI अंतर्दृष्टि से विचार जनरेट करें।"],
    ["Go to AI Insights", "Ir a análisis de IA", "Accéder aux analyses IA", "AI अंतर्दृष्टि पर जाएँ"],
    ["Priority:", "Prioridad:", "Priorité :", "प्राथमिकता:"],
    ["Status updated.", "Estado actualizado.", "Statut mis à jour.", "स्थिति अपडेट हुई।"],
    ["Saved.", "Guardado.", "Enregistré.", "सहेजा गया।"],
    ["Generate Report", "Generar informe", "Générer un rapport", "रिपोर्ट बनाएँ"],
    ["Generating…", "Generando…", "Génération…", "बनाया जा रहा है…"],
    ["Select an analyzed dataset first.", "Primero selecciona un conjunto de datos analizado.", "Sélectionnez d'abord un jeu de données analysé.", "पहले विश्लेषित डेटासेट चुनें।"],
    ["Report generated.", "Informe generado.", "Rapport généré.", "रिपोर्ट बन गई।"],
    ["No reports yet", "Aún no hay informes", "Aucun rapport pour le moment", "अभी कोई रिपोर्ट नहीं"],
    ["Generate a report to get an exportable summary of KPIs, funnel, segments, and AI insights.", "Genera un informe para obtener un resumen exportable de KPI, embudo, segmentos y análisis de IA.", "Générez un rapport pour obtenir un récapitulatif exportable des KPI, de l'entonnoir, des segments et des analyses IA.", "KPI, फ़नल, सेगमेंट और AI अंतर्दृष्टि का निर्यात योग्य सारांश पाने के लिए रिपोर्ट बनाएँ।"],
    ["Export CSV", "Exportar CSV", "Exporter en CSV", "CSV निर्यात करें"],
    ["Export Excel", "Exportar Excel", "Exporter vers Excel", "Excel निर्यात करें"],
    ["Export PDF", "Exportar PDF", "Exporter en PDF", "PDF निर्यात करें"],
    ["Export failed.", "Error al exportar.", "Échec de l'exportation.", "निर्यात विफल हुआ।"],
    ["Settings &", "Configuración y", "Paramètres et", "सेटिंग्स और"],
    ["preferences.", "preferencias.", "préférences.", "प्राथमिकताएँ।"],
    ["Manage account security, activity, and how your workspace is displayed.", "Administra la seguridad de tu cuenta, la actividad y la visualización del espacio de trabajo.", "Gérez la sécurité de votre compte, l'activité et l'affichage de votre espace de travail.", "खाता सुरक्षा, गतिविधि और वर्कस्पेस प्रदर्शन प्रबंधित करें।"],
    ["Account details", "Detalles de la cuenta", "Détails du compte", "खाता विवरण"],
    ["Your profile and workspace information", "Información de tu perfil y espacio de trabajo", "Informations sur votre profil et votre espace de travail", "आपकी प्रोफ़ाइल और वर्कस्पेस जानकारी"],
    ["Email address", "Correo electrónico", "Adresse e-mail", "ईमेल पता"],
    ["Organization", "Organización", "Organisation", "संगठन"],
    ["API connection", "Conexión API", "Connexion API", "API कनेक्शन"],
    ["Password & security", "Contraseña y seguridad", "Mot de passe et sécurité", "पासवर्ड और सुरक्षा"],
    ["Change your password to keep your account secure", "Cambia tu contraseña para proteger tu cuenta", "Modifiez votre mot de passe pour sécuriser votre compte", "अपने खाते को सुरक्षित रखने के लिए पासवर्ड बदलें"],
    ["Current password", "Contraseña actual", "Mot de passe actuel", "वर्तमान पासवर्ड"],
    ["New password", "Nueva contraseña", "Nouveau mot de passe", "नया पासवर्ड"],
    ["Confirm new password", "Confirmar nueva contraseña", "Confirmer le nouveau mot de passe", "नए पासवर्ड की पुष्टि करें"],
    ["At least 8 characters", "Al menos 8 caracteres", "Au moins 8 caractères", "कम से कम 8 अक्षर"],
    ["Enter your new password again", "Vuelve a introducir tu nueva contraseña", "Saisissez à nouveau votre nouveau mot de passe", "नया पासवर्ड फिर से दर्ज करें"],
    ["Use at least 8 characters.", "Usa al menos 8 caracteres.", "Utilisez au moins 8 caractères.", "कम से कम 8 अक्षरों का उपयोग करें।"],
    ["Update password", "Actualizar contraseña", "Mettre à jour le mot de passe", "पासवर्ड अपडेट करें"],
    ["The new passwords do not match.", "Las nuevas contraseñas no coinciden.", "Les nouveaux mots de passe ne correspondent pas.", "नए पासवर्ड मेल नहीं खाते।"],
    ["Your password was updated.", "Tu contraseña se ha actualizado.", "Votre mot de passe a été mis à jour.", "आपका पासवर्ड अपडेट हो गया।"],
    ["Past activity", "Actividad reciente", "Activité récente", "पिछली गतिविधि"],
    ["Recent activity saved in this browser for your account", "Actividad reciente de tu cuenta guardada en este navegador", "Activité récente de votre compte enregistrée dans ce navigateur", "आपके खाते की हालिया गतिविधि इस ब्राउज़र में सहेजी गई"],
    ["No activity recorded yet", "Aún no hay actividad registrada", "Aucune activité enregistrée pour le moment", "अभी कोई गतिविधि दर्ज नहीं हुई"],
    ["Sign-ins, dataset uploads, and key actions will appear here.", "Aquí aparecerán los inicios de sesión, las cargas de datos y las acciones importantes.", "Les connexions, imports de données et actions importantes apparaîtront ici.", "साइन-इन, डेटासेट अपलोड और मुख्य कार्रवाइयाँ यहाँ दिखेंगी।"],
    ["Activity is stored locally in this browser and is not shared with other devices.", "La actividad se guarda en este navegador y no se comparte con otros dispositivos.", "L'activité est stockée dans ce navigateur et n'est pas partagée avec d'autres appareils.", "गतिविधि इसी ब्राउज़र में सहेजी जाती है और अन्य डिवाइस के साथ साझा नहीं होती।"],
    ["Language & region", "Idioma y región", "Langue et région", "भाषा और क्षेत्र"],
    ["Choose how dates and numbers are formatted", "Elige el formato de fechas y números", "Choisissez le format des dates et des nombres", "तारीख़ और संख्याओं का प्रारूप चुनें"],
    ["Formatting preference", "Preferencia de formato", "Préférence de format", "फ़ॉर्मेटिंग प्राथमिकता"],
    ["The selected language changes the entire interface, including pages, controls, and messages.", "El idioma seleccionado cambia toda la interfaz, incluidas las páginas, los controles y los mensajes.", "La langue sélectionnée modifie toute l'interface, y compris les pages, les commandes et les messages.", "चुनी गई भाषा पूरे इंटरफ़ेस, पृष्ठों, नियंत्रणों और संदेशों को बदलती है।"],
    ["English", "Inglés", "Anglais", "अंग्रेज़ी"],
    ["Hindi", "Hindi", "Hindi", "हिन्दी"],
    ["Spanish", "Español", "Espagnol", "स्पैनिश"],
    ["French", "Francés", "Français", "फ़्रेंच"],
    ["This changes date and number formatting. App text is currently available in English.", "El idioma elegido cambia toda la interfaz, incluidas las páginas, los controles y los mensajes.", "La langue choisie modifie toute l'interface, y compris les pages, les commandes et les messages.", "चुनी हुई भाषा पूरे इंटरफ़ेस, पृष्ठों, नियंत्रणों और संदेशों को बदलती है।"],
    ["Help & support", "Ayuda y soporte", "Aide et assistance", "सहायता और समर्थन"],
    ["Find guidance or get help with your workspace", "Encuentra orientación o ayuda para tu espacio de trabajo", "Trouvez des conseils ou de l'aide pour votre espace de travail", "अपने वर्कस्पेस के लिए मार्गदर्शन या सहायता पाएँ"],
    ["API documentation", "Documentación de la API", "Documentation de l'API", "API दस्तावेज़"],
    ["Browse available backend endpoints", "Consulta los endpoints disponibles del backend", "Consultez les points de terminaison du serveur", "उपलब्ध बैकएंड एंडपॉइंट देखें"],
    ["Having trouble with a dataset?", "¿Problemas con un conjunto de datos?", "Un problème avec un jeu de données ?", "डेटासेट में समस्या है?"],
    ["Check that the file has headers and map the relevant columns before running analysis.", "Comprueba que el archivo tenga encabezados y asigna las columnas relevantes antes del análisis.", "Vérifiez que le fichier comporte des en-têtes et associez les colonnes pertinentes avant l'analyse.", "विश्लेषण से पहले जाँचें कि फ़ाइल में हेडर हैं और संबंधित कॉलम मैप करें।"],
    ["Need account help?", "¿Necesitas ayuda con la cuenta?", "Besoin d'aide pour votre compte ?", "खाते में सहायता चाहिए?"],
    ["Contact your workspace administrator for access or organization support.", "Contacta con el administrador de tu espacio de trabajo para obtener ayuda con el acceso o la organización.", "Contactez l'administrateur de votre espace de travail pour toute question d'accès ou d'organisation.", "पहुँच या संगठन संबंधी सहायता के लिए वर्कस्पेस व्यवस्थापक से संपर्क करें।"],
    ["Formatting preference set to", "Idioma de la aplicación cambiado a", "Langue de l'application définie sur", "ऐप की भाषा बदलकर"],
    ["Changed number and date format to", "Cambió el idioma de la aplicación a", "Langue de l'application modifiée en", "ऐप की भाषा बदली"],
    ["Selected dataset", "Conjunto de datos seleccionado", "Jeu de données sélectionné", "डेटासेट चुना"],
    ["Signed out", "Sesión cerrada", "Déconnexion", "साइन आउट किया"],
    ["Signed in", "Sesión iniciada", "Connexion", "साइन इन किया"],
    ["Created a workspace", "Se creó un espacio de trabajo", "Espace de travail créé", "वर्कस्पेस बनाया"],
    ["Changed account password", "Se cambió la contraseña de la cuenta", "Mot de passe du compte modifié", "खाते का पासवर्ड बदला"],
    ["Changed app language", "Se cambió el idioma de la aplicación", "Langue de l'application modifiée", "ऐप की भाषा बदली"],
    ["App language updated.", "Idioma de la aplicación actualizado.", "Langue de l'application mise à jour.", "ऐप की भाषा अपडेट हुई।"],
  ];

  const codes = ["es", "fr", "hi"];
  const dictionaries = Object.fromEntries(codes.map((code, column) => [
    code,
    Object.fromEntries(rows.map((row) => [row[0], row[column + 1]])),
  ]));
  const locales = { en: "en-US", es: "es-ES", fr: "fr-FR", hi: "hi-IN" };
  const languageNames = { en: "English", es: "Spanish", fr: "French", hi: "Hindi" };
  const originalText = new WeakMap();
  const originalAttributes = new WeakMap();

  function getLanguage() {
    const language = localStorage.getItem("growth_intel_language") || "en";
    return dictionaries[language] ? language : "en";
  }

  function translateDynamicText(text, language) {
    const numberTranslations = {
      es: { rows: "filas", total: "en total", records: "registros seguidos en cada etapa", leads: "clientes potenciales", page: "Página", of: "de" },
      fr: { rows: "lignes", total: "au total", records: "enregistrements suivis à chaque étape", leads: "prospects", page: "Page", of: "sur" },
      hi: { rows: "पंक्तियाँ", total: "कुल", records: "रिकॉर्ड हर चरण में ट्रैक किए गए", leads: "लीड", page: "पृष्ठ", of: "में से" },
    }[language];
    if (!numberTranslations) return text;

    let match = text.match(/^([\d.,]+) rows total$/);
    if (match) return `${match[1]} ${numberTranslations.rows} ${numberTranslations.total}`;
    match = text.match(/^([\d.,]+) rows$/);
    if (match) return `${match[1]} ${numberTranslations.rows}`;
    match = text.match(/^([\d.,]+) leads$/);
    if (match) return `${match[1]} ${numberTranslations.leads}`;
    match = text.match(/^([\d.,]+) records tracked through each stage$/);
    if (match) return `${match[1]} ${numberTranslations.records}`;
    match = text.match(/^Page (\d+) of (\d+)$/);
    if (match) return `${numberTranslations.page} ${match[1]} ${numberTranslations.of} ${match[2]}`;
    return text.replace(/ rows(?=\))/g, ` ${numberTranslations.rows})`);
  }

  function translateNode(node, language) {
    if (!originalText.has(node)) originalText.set(node, node.nodeValue);
    const original = originalText.get(node);
    const trimmed = original.trim();
    const translated = dictionaries[language]?.[trimmed] || translateDynamicText(trimmed, language);
    const leading = original.match(/^\s*/)?.[0] || "";
    const trailing = original.match(/\s*$/)?.[0] || "";
    node.nodeValue = `${leading}${translated}${trailing}`;
  }

  function translateElement(element, language) {
    const walker = document.createTreeWalker(element, NodeFilter.SHOW_TEXT);
    let node;
    while ((node = walker.nextNode())) translateNode(node, language);

    const translatableAttributes = ["placeholder", "aria-label", "title"];
    element.querySelectorAll("*").forEach((child) => {
      translatableAttributes.forEach((name) => {
        if (!child.hasAttribute(name)) return;
        let saved = originalAttributes.get(child);
        if (!saved) {
          saved = {};
          originalAttributes.set(child, saved);
        }
        if (!(name in saved)) saved[name] = child.getAttribute(name);
        child.setAttribute(name, dictionaries[language]?.[saved[name]] || saved[name]);
      });
    });

    translatableAttributes.forEach((name) => {
      if (!element.hasAttribute(name)) return;
      let saved = originalAttributes.get(element);
      if (!saved) {
        saved = {};
        originalAttributes.set(element, saved);
      }
      if (!(name in saved)) saved[name] = element.getAttribute(name);
      element.setAttribute(name, dictionaries[language]?.[saved[name]] || saved[name]);
    });
    document.documentElement.lang = language;
    document.title = dictionaries[language]?.["Growth & Lead Intelligence Platform"] || "Growth & Lead Intelligence Platform";
  }

  const observer = new MutationObserver((mutations) => {
    const language = getLanguage();
    for (const mutation of mutations) {
      mutation.addedNodes.forEach((node) => {
        if (node.nodeType === Node.TEXT_NODE) translateNode(node, language);
        else if (node.nodeType === Node.ELEMENT_NODE) translateElement(node, language);
      });
    }
  });
  observer.observe(document.documentElement, { childList: true, subtree: true });

  window.GrowthI18n = {
    getLanguage,
    getLocale: () => locales[getLanguage()],
    getLanguageName: (code) => languageNames[code] || languageNames.en,
    translateText: (text) => dictionaries[getLanguage()]?.[text] || translateDynamicText(text, getLanguage()),
    translate: (element = document.getElementById("app")) => {
      if (element) translateElement(element, getLanguage());
    },
    setLanguage: (language) => {
      localStorage.setItem("growth_intel_language", language);
      document.documentElement.lang = language;
    },
  };
})();

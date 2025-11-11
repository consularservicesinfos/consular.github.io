import streamlit as st
import requests
import json
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import jinja2
import os
from PIL import Image

GMAIL_USER = "consular.services.infos@gmail.com"
GMAIL_PASSWORD = "ocwo vozn pskp copd"

# CSS commun pour l'application
COMMON_CSS = """
<style>
    /* ------------------- Variable de couleur principale ------------------- */
    :root {
        --primary-color: #173887;
        --secondary-color: #2a5298;
        --light-color: #ffffff;
        --danger-color: #dc3545;
        --success-color: #28a745;
        --warning-color: #ffc107;
    }
    
    /* ------------------- Style Global ------------------- */
    .main-header {
        font-size: 2.5rem;
        color: var(--primary-color);
        text-align: center;
        margin-bottom: 2rem;
        font-weight: 700;
    }
    
    .section-header {
        color: var(--primary-color);
        border-bottom: 2px solid var(--primary-color);
        padding-bottom: 10px;
        margin-bottom: 20px;
        font-size: 1.4rem;
        font-weight: 600;
    }
    
    /* ------------------- Style Global des Boutons ------------------- */
    .stButton > button {
        background-color: var(--primary-color) !important;
        color: var(--light-color) !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        transition: all 0.3s ease !important;
    }
    
    .stButton > button:hover {
        background-color: var(--secondary-color) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(23, 56, 135, 0.3) !important;
    }
    
    /* Bouton de déconnexion */
    .logout-btn > button {
        background-color: var(--danger-color) !important;
    }
    
    .logout-btn > button:hover {
        background-color: #c82333 !important;
    }
    
    /* ------------------- Messages d'alerte ------------------- */
    .success-message {
        background-color: #d4edda;
        color: var(--success-color);
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #c3e6cb;
        margin: 10px 0;
    }
    
    .error-message {
        background-color: #f8d7da;
        color: var(--danger-color);
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #f5c6cb;
        margin: 10px 0;
    }
    
    .warning-message {
        background-color: #fff3cd;
        color: #856404;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #ffeaa7;
        margin: 10px 0;
    }
    
    /* ------------------- Champs de formulaire ------------------- */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        border: 2px solid #e9ecef !important;
        border-radius: 8px !important;
        padding: 12px !important;
        font-size: 14px !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: var(--primary-color) !important;
        box-shadow: 0 0 0 0.2rem rgba(23, 56, 135, 0.25) !important;
    }
    
    /* ------------------- Onglets ------------------- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f8f9fa;
        border-radius: 8px 8px 0px 0px;
        gap: 8px;
        padding: 12px 24px;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--primary-color) !important;
        color: white !important;
    }
</style>
"""

# CSS pour la page de connexion
LOGIN_CSS = """
<style>
    .login-main {
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        min-height: 100vh;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 20px;
    }
    
    .login-container {
        background: var(--light-color);
        border-radius: 20px;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
        overflow: hidden;
        max-width: 900px;
        width: 100%;
    }
    
    .login-logo-section {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 50px 30px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
    }
    
    .login-form-section {
        padding: 50px 40px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .login-title {
        color: #173887;
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 10px;
        text-align: center;
    }
    
    .login-subtitle {
        color: #6c757d;
        font-size: 1.1rem;
        margin-bottom: 40px;
        text-align: center;
    }
    
    .login-error {
        background-color: #f8d7da;
        color: var(--danger-color);
        padding: 12px;
        border-radius: 8px;
        border: 1px solid #f5c6cb;
        margin: 15px 0;
        text-align: center;
        font-weight: 500;
    }
    
    /* Style personnalisé pour les boutons de login */
    .login-button {
        background-color: #173887 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        width: 100% !important;
    }
    
    .login-button:hover {
        background-color: #03143d !important;
    }
    
    .cancel-button {
        background-color: #03143d !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        width: 100% !important;
    }
    
    .cancel-button:hover {
        background-color: #173887 !important;
    }
</style>
"""

def check_authentication():
    """Vérifie si l'utilisateur est authentifié"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        show_login_page()
        return False
    return True

def show_login_page():
    """Affiche la page de connexion avec le nouveau layout et style"""
    st.set_page_config(
        page_title="Connexion - Consular Services",
        page_icon="🔐",
        layout="centered"
    )
    
    
    
    # Deux colonnes internes pour le logo et le formulaire
    col_logo, col_form = st.columns([1, 1.2])
    
    with col_logo:
        st.markdown('<div class="login-logo-section">', unsafe_allow_html=True)
        
        # Affichage du logo
        try:
            logo = Image.open("Logo.png")
            st.image(logo, width=240)
        except FileNotFoundError:
            st.markdown('<div style="font-size: 80px; color: var(--primary-color); margin-bottom: 20px;">🔐</div>', unsafe_allow_html=True)
        except Exception as e:
            st.markdown(f'<div style="color: var(--danger-color); text-align: center;">Erreur logo</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

    with col_form:
        st.markdown('<div class="login-form-section">', unsafe_allow_html=True)
        
        st.markdown("""
            <h2 style="color: #173887; font-weight: 600; margin: 15px 0 10px 0; text-align: center;">
                Consular Services
            </h2>
           
        """, unsafe_allow_html=True)
        
        # Formulaire de connexion
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input(
                "Nom d'utilisateur", 
                placeholder="Entrez votre nom d'utilisateur",
                label_visibility="collapsed"
            )
            
            password = st.text_input(
                "Mot de passe", 
                type="password", 
                placeholder="Entrez votre mot de passe",
                label_visibility="collapsed"
            )
            
            # Boutons côte à côte
            col_cancel, col_submit = st.columns(2)
            
            with col_cancel:
                # Bouton Annuler avec style personnalisé
                st.markdown("""
                    <style>
                    div[data-testid="stForm"] div:has(> div[data-testid="baseButton-secondary"]) button {
                        background-color: #03143d !important;
                        color: white !important;
                        border: none !important;
                        border-radius: 8px !important;
                        padding: 12px 24px !important;
                        font-weight: 600 !important;
                        width: 100% !important;
                    }
                    div[data-testid="stForm"] div:has(> div[data-testid="baseButton-secondary"]) button:hover {
                        background-color: #173887 !important;
                    }
                    </style>
                """, unsafe_allow_html=True)
                cancel_clicked = st.form_submit_button(
                    "Annuler", 
                    use_container_width=True
                )
            
            with col_submit:
                # Bouton Se connecter avec style personnalisé
                st.markdown("""
                    <style>
                    div[data-testid="stForm"] div:has(> div[data-testid="baseButton-primary"]) button {
                        background-color: #173887 !important;
                        color: white !important;
                        border: none !important;
                        border-radius: 8px !important;
                        padding: 12px 24px !important;
                        font-weight: 600 !important;
                        width: 100% !important;
                    }
                    div[data-testid="stForm"] div:has(> div[data-testid="baseButton-primary"]) button:hover {
                        background-color: #03143d !important;
                    }
                    </style>
                """, unsafe_allow_html=True)
                submit_clicked = st.form_submit_button(
                    "Se connecter", 
                    use_container_width=True
                )
            
            if submit_clicked:
                if username == "Admin" and password == "Admin":
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.markdown(
                        '<div class="login-error">Identifiants incorrects. Utilisez Admin/Admin</div>', 
                        unsafe_allow_html=True
                    )

        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    return False

def test_gmail_connection():
    """Teste la connexion à Gmail"""
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.quit()
        return True, "Connexion Gmail réussie"
    except smtplib.SMTPAuthenticationError:
        return False, "Erreur d'authentification. Vérifiez le mot de passe d'application."
    except Exception as e:
        return False, f"Erreur de connexion: {str(e)}"

def send_email_direct(to_email, subject, template_vars):
    """Envoie un email directement via Gmail"""
    try:
        # Template HTML avec logo intégré
        EMAIL_TEMPLATE = """
        <!DOCTYPE html>
        <html lang="fr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Email Consular Services</title>
            <style>
                * { margin: 0; padding: 0; box-sizing: border-box; }
                body { 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                    line-height: 1.6; color: #333; background-color: #f4f4f4; padding: 20px;
                }
                .email-container {
                    max-width: 600px; margin: 0 auto; background: #ffffff; 
                    border-radius: 10px; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }
                .header {
                    background: linear-gradient(135deg, #173887 0%, #2a5298 100%);
                    color: white; padding: 30px; text-align: center;
                }
                .logo-header {
                    max-width: 120px;
                    margin-bottom: 15px;
                }
                .header h1 { font-size: 24px; margin-bottom: 10px; font-weight: 600; }
                .header .subject { font-size: 16px; opacity: 0.9; font-weight: 300; }
                .content { padding: 30px; }
                .greeting { font-size: 16px; margin-bottom: 20px; color: #555; }
                .message-content { font-size: 14px; line-height: 1.7; color: #444; margin-bottom: 25px; }
                .message-content p { margin-bottom: 15px; }
                .button-container { text-align: center; margin: 25px 0; }
                .cta-button {
                    display: inline-block; background: linear-gradient(135deg, #173887 0%, #2a5298 100%);
                    color: white; padding: 12px 30px; text-decoration: none; border-radius: 25px;
                    font-weight: 500; font-size: 14px; transition: transform 0.3s ease, box-shadow 0.3s ease;
                }
                .cta-button:hover { transform: translateY(-2px); box-shadow: 0 6px 12px rgba(23, 56, 135, 0.3); }
                .signature { margin-top: 30px; padding-top: 20px; border-top: 1px solid #eaeaea; }
                .signature p { margin-bottom: 8px; color: #555; }
                .sender-name { font-weight: 600; color: #173887 !important; font-size: 16px; }
                .footer { background: #f8f9fa; padding: 20px 30px; text-align: center; color: #666; font-size: 12px; }
                .contact-info { margin: 10px 0; line-height: 1.5; }
                .info-box {
                    background: #f8f9fa; border-left: 4px solid #173887; padding: 15px;
                    margin: 15px 0; border-radius: 0 8px 8px 0;
                }
                .info-box h3 { color: #173887; margin-bottom: 8px; font-size: 14px; }
                @media (max-width: 600px) {
                    .content { padding: 20px; }
                    .header { padding: 20px; }
                    .header h1 { font-size: 20px; }
                }
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="header">
                    {% if logo_base64 %}
                    <img src="{{ logo_base64 }}" alt="Logo Consular Services" class="logo-header">
                    {% endif %}
                    <h1>{{company_name}}</h1>
                    <div class="subject">{{email_subject}}</div>
                </div>
                
                <div class="content">
                    <div class="greeting">
                        <strong>Bonjour {{recipient_name}},</strong>
                    </div>
                    
                    <div class="message-content">
                        {{message_content|safe}}
                    </div>
                    
                    {% if additional_info %}
                    <div class="info-box">
                        <h3>Informations importantes</h3>
                        {{additional_info|safe}}
                    </div>
                    {% endif %}
                    
                    {% if call_to_action_url and call_to_action_text %}
                    <div class="button-container">
                        <a href="{{call_to_action_url}}" class="cta-button">
                            {{call_to_action_text}}
                        </a>
                    </div>
                    {% endif %}
                    
                    <div class="signature">
                        <p class="sender-name">{{sender_name}}</p>
                        <p><strong>{{company_name}}</strong></p>
                        <p>Email: {{contact_email}}</p>
                        <p>Téléphone: {{contact_phone}}</p>
                        {% if department %}
                        <p>Département: {{department}}</p>
                        {% endif %}
                    </div>
                </div>
                
                <div class="footer">
                    <div class="contact-info">
                        <strong>{{company_name}}</strong><br>
                        {{company_address}}
                    </div>
                    
                    <div style="margin-top: 10px; font-size: 11px; color: #999;">
                        &copy; 2024 {{company_name}}. Tous droits réservés.
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

        # Encoder le logo en base64 pour l'inclure dans l'email
        logo_base64 = None
        try:
            with open("Logo.png", "rb") as logo_file:
                import base64
                logo_base64 = base64.b64encode(logo_file.read()).decode()
                logo_base64 = f"data:image/png;base64,{logo_base64}"
        except:
            logo_base64 = None

        # Rendre le template
        template_env = jinja2.Environment(loader=jinja2.BaseLoader())
        template = template_env.from_string(EMAIL_TEMPLATE)
        html_content = template.render(logo_base64=logo_base64, **template_vars)
        
        # Création du message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{template_vars.get('company_name', 'Consular Services')} <{GMAIL_USER}>"
        msg['To'] = to_email
        
        # Version texte simple
        text_content = f"""
        {template_vars.get('company_name', 'Consular Services')}
        
        Bonjour {template_vars.get('recipient_name', '')},
        
        {template_vars.get('message_content', '').replace('<br>', '\n').replace('<p>', '\n').replace('</p>', '\n')}
        
        {template_vars.get('additional_info', '').replace('<br>', '\n').replace('<p>', '\n').replace('</p>', '\n')}
        
        Cordialement,
        {template_vars.get('sender_name', 'Équipe Consular Services')}
        {template_vars.get('company_name', 'Consular Services')}
        Email: {template_vars.get('contact_email', 'consular.services.infos@gmail.com')}
        Téléphone: {template_vars.get('contact_phone', '')}
        """
        
        # Attacher les versions
        msg.attach(MIMEText(text_content, 'plain'))
        msg.attach(MIMEText(html_content, 'html'))
        
        # Connexion et envoi
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        return True, f"Email envoyé avec succès à {to_email}"
        
    except smtplib.SMTPAuthenticationError:
        return False, "Erreur d'authentification. Vérifiez le mot de passe d'application."
    except Exception as e:
        return False, f"Erreur lors de l'envoi: {str(e)}"

def main_app():
    """Interface principale après authentification"""
    st.set_page_config(
        page_title="Consular Services - Envoi d'Emails",
        page_icon="📧",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Application du CSS commun
    st.markdown(COMMON_CSS, unsafe_allow_html=True)

    # Header avec bouton de déconnexion
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        st.markdown('<div class="main-header">Consular Services - Plateforme d\'envoi d\'emails</div>', unsafe_allow_html=True)
    
    

    # Sidebar
    with st.sidebar:
    # Logo dans la sidebar - avec gestion d'erreur
        try:
            logo = Image.open("Logo.png")
            st.image(logo, use_container_width=True)
        except FileNotFoundError:
            st.markdown('<div style="font-size: 40px; color: var(--primary-color); text-align: center; margin: 20px 0;">📧</div>', unsafe_allow_html=True)
            st.sidebar.info("Logo non trouvé - utilisation de l'emoji")
        except Exception as e:
            st.markdown('<div style="font-size: 40px; color: var(--primary-color); text-align: center; margin: 20px 0;">📧</div>', unsafe_allow_html=True)
            st.sidebar.warning("Erreur lors du chargement du logo")
       
        
        st.markdown("---")
        st.subheader("Informations par défaut")
        
        default_company = st.text_input("Nom de l'entreprise", value="Services Consulaires France")
        default_sender = st.text_input("Nom de l'expéditeur", value="Service Consulaire")
        default_contact_email = st.text_input("Email de contact", value="consular.services.infos@gmail.com")
        default_phone = st.text_input("Téléphone", value="+33 1 45 67 89 00")
        default_address = st.text_input("Adresse", value="123 Avenue des Diplomates, 75008 Paris, France")
        st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
        if st.button("Déconnexion", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Interface principale
    tab1, tab2, tab3 = st.tabs(["Composition", "Prévisualisation", "Historique"])

    with tab1:
        # Test initial de connexion
        connection_success, connection_message = test_gmail_connection()
        if not connection_success:
            st.markdown(f'<div class="warning-message">{connection_message}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="success-message">{connection_message}</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown('<div class="section-header">Destinataire et Sujet</div>', unsafe_allow_html=True)
            
            to_email = st.text_input("Email du destinataire*", placeholder="exemple@email.com", key="to_email")
            recipient_name = st.text_input("Nom du destinataire*", placeholder="Jean Dupont", key="recipient_name")
            subject = st.text_input("Objet de l'email*", placeholder="Confirmation de rendez-vous consulaire", key="subject")
            
            st.markdown('<div class="section-header">Contenu principal</div>', unsafe_allow_html=True)
            
            message_content = st.text_area(
                "Message principal*", 
                height=150,
                placeholder="Nous confirmons votre rendez-vous pour le 25 novembre 2024 à 10h30.\n\nVotre dossier a été préalablement examiné et est complet.\n\nMerci de vous présenter 15 minutes avant l'heure du rendez-vous.",
                key="message_content"
            )
            
            additional_info = st.text_area(
                "Informations supplémentaires", 
                height=100,
                placeholder="Lieu : Ambassade de France, Service Consulaire\nAdresse : 123 Avenue des Diplomates, 75008 Paris\n\nDocuments à apporter :\n- Passeport original\n- 2 photos d'identité",
                key="additional_info"
            )

        with col2:
            st.markdown('<div class="section-header">Personnalisation</div>', unsafe_allow_html=True)
            
            company_name = st.text_input("Nom de l'entreprise", value=default_company, key="company_name")
            sender_name = st.text_input("Nom de l'expéditeur", value=default_sender, key="sender_name")
            contact_email = st.text_input("Email de contact", value=default_contact_email, key="contact_email")
            contact_phone = st.text_input("Téléphone de contact", value=default_phone, key="contact_phone")
            department = st.text_input("Département/Service", placeholder="Service des Visas", key="department")
            company_address = st.text_input("Adresse", value=default_address, key="company_address")
            
            st.markdown('<div class="section-header">Appel à l\'action</div>', unsafe_allow_html=True)
            
            call_to_action_url = st.text_input("URL du bouton", placeholder="https://exemple.com/confirmation", key="call_to_action_url")
            call_to_action_text = st.text_input("Texte du bouton", placeholder="Confirmer mon rendez-vous", key="call_to_action_text")
            
            # Bouton d'envoi
            st.markdown("---")
            
            if st.button("Envoyer l'email", type="primary", use_container_width=True, disabled=not connection_success):
                if not all([to_email, recipient_name, subject, message_content]):
                    st.markdown('<div class="error-message">Veuillez remplir tous les champs obligatoires (*)</div>', unsafe_allow_html=True)
                else:
                    # Préparation des données
                    template_vars = {
                        'company_name': company_name,
                        'email_subject': subject,
                        'recipient_name': recipient_name,
                        'message_content': message_content.replace('\n', '<br>'),
                        'additional_info': additional_info.replace('\n', '<br>') if additional_info else "",
                        'sender_name': sender_name,
                        'contact_email': contact_email,
                        'contact_phone': contact_phone,
                        'department': department,
                        'company_address': company_address,
                        'call_to_action_url': call_to_action_url,
                        'call_to_action_text': call_to_action_text
                    }
                    
                    with st.spinner("Envoi en cours..."):
                        success, message = send_email_direct(to_email, subject, template_vars)
                    
                    if success:
                        st.markdown(f'<div class="success-message">{message}</div>', unsafe_allow_html=True)
                        if 'sent_emails' not in st.session_state:
                            st.session_state.sent_emails = []
                        st.session_state.sent_emails.append({
                            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            'to_email': to_email,
                            'subject': subject,
                            'recipient_name': recipient_name,
                            'success': True
                        })
                    else:
                        st.markdown(f'<div class="error-message">{message}</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="section-header">Aperçu de l\'email</div>', unsafe_allow_html=True)
        
        # Récupération des valeurs directement depuis les champs
        current_values = {
            'company_name': st.session_state.get('company_name', default_company),
            'sender_name': st.session_state.get('sender_name', default_sender),
            'contact_email': st.session_state.get('contact_email', default_contact_email),
            'contact_phone': st.session_state.get('contact_phone', default_phone),
            'department': st.session_state.get('department', ""),
            'company_address': st.session_state.get('company_address', default_address),
            'subject': st.session_state.get('subject', ""),
            'recipient_name': st.session_state.get('recipient_name', ""),
            'message_content': st.session_state.get('message_content', ""),
            'additional_info': st.session_state.get('additional_info', ""),
            'call_to_action_url': st.session_state.get('call_to_action_url', ""),
            'call_to_action_text': st.session_state.get('call_to_action_text', "")
        }

        if not all([current_values['subject'], current_values['recipient_name'], current_values['message_content']]):
            st.warning("Veuillez d'abord remplir les champs obligatoires dans l'onglet 'Composition'")
        else:
            # Encoder le logo pour la prévisualisation
            logo_base64 = None
            try:
                with open("Logo.png", "rb") as logo_file:
                    import base64
                    logo_base64 = base64.b64encode(logo_file.read()).decode()
                    logo_base64 = f"data:image/png;base64,{logo_base64}"
            except:
                logo_base64 = None

            preview_data = {
                "company_name": current_values['company_name'],
                "subject": current_values['subject'],
                "recipient_name": current_values['recipient_name'],
                "message_content": current_values['message_content'].replace('\n', '<br>'),
                "additional_info": current_values['additional_info'].replace('\n', '<br>') if current_values['additional_info'] else "",
                "sender_name": current_values['sender_name'],
                "contact_email": current_values['contact_email'],
                "contact_phone": current_values['contact_phone'],
                "call_to_action_url": current_values['call_to_action_url'],
                "call_to_action_text": current_values['call_to_action_text']
            }
            
            html_preview = f"""
            <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 600px; margin: 0 auto;">
                <div style="background: linear-gradient(135deg, #173887 0%, #2a5298 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                    {f'<img src="{logo_base64}" alt="Logo" style="max-width: 120px; margin-bottom: 15px;">' if logo_base64 else ''}
                    <h1 style="margin: 0; font-size: 24px;">{preview_data['company_name']}</h1>
                    <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">{preview_data['subject']}</p>
                </div>
                
                <div style="padding: 30px; background: white; border-radius: 0 0 10px 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <p style="font-size: 16px; margin-bottom: 20px;"><strong>Bonjour {preview_data['recipient_name']},</strong></p>
                    
                    <div style="font-size: 14px; line-height: 1.7; margin-bottom: 25px;">
                        {preview_data['message_content']}
                    </div>
                    
                    {f'<div style="background: #f8f9fa; border-left: 4px solid #173887; padding: 15px; margin: 15px 0; border-radius: 0 8px 8px 0;"><strong>Informations importantes:</strong><br>{preview_data.get("additional_info", "")}</div>' if preview_data.get('additional_info') else ''}
                    
                    {f'<div style="text-align: center; margin: 25px 0;"><a href="{preview_data["call_to_action_url"]}" style="background: linear-gradient(135deg, #173887 0%, #2a5298 100%); color: white; padding: 12px 30px; text-decoration: none; border-radius: 25px; display: inline-block;">{preview_data["call_to_action_text"]}</a></div>' if preview_data.get('call_to_action_url') and preview_data.get('call_to_action_text') else ''}
                    
                    <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eaeaea;">
                        <p style="margin: 5px 0; color: #173887; font-weight: 600;">{preview_data['sender_name']}</p>
                        <p style="margin: 5px 0;">{preview_data['company_name']}</p>
                        <p style="margin: 5px 0;">Email: {preview_data['contact_email']}</p>
                        <p style="margin: 5px 0;">Téléphone: {preview_data['contact_phone']}</p>
                    </div>
                </div>
                <div style="background: #f8f9fa; padding: 20px 30px; text-align: center; color: #666; font-size: 12px; border-radius: 0 0 10px 10px;">
                    {current_values['company_address']}
                </div>
            </div>
            """
            st.components.v1.html(html_preview, height=600, scrolling=True)

    with tab3:
        st.markdown('<div class="section-header">Historique des envois</div>', unsafe_allow_html=True)
        
        if 'sent_emails' not in st.session_state or not st.session_state.sent_emails:
            st.info("Aucun email envoyé pour le moment")
        else:
            # Préparer les données pour l'affichage
            emails_data = list(reversed(st.session_state.sent_emails))
            
            # Afficher sous forme de tableau
            for i, email in enumerate(emails_data):
                with st.container():
                    col1, col2, col3 = st.columns([2, 2, 1])
                    
                    with col1:
                        st.write(f"**À:** {email['to_email']}")
                        st.write(f"**Nom:** {email['recipient_name']}")
                    
                    with col2:
                        st.write(f"**Sujet:** {email['subject']}")
                        st.write(f"**Date:** {email['timestamp']}")
                    
                    with col3:
                        if email['success']:
                            st.success("Envoyé")
                        else:
                            st.error("Échec")
                    
                    if i < len(emails_data) - 1:
                        st.markdown("---")

    # Footer
    st.markdown("---")
    st.markdown(
        
        "Consular Services Email Platform • "
        "consular.services.infos@gmail.com • "
        f"© {datetime.now().year} Tous droits réservés"
        "</div>", 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    if check_authentication():
        main_app()
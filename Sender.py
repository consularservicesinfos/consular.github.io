import streamlit as st
import requests
import json
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import base64
import os
from pathlib import Path
from PIL import Image

GMAIL_USER = os.environ.get("GMAIL_USER", "consular.services.infos@gmail.com")
GMAIL_PASSWORD = os.environ.get("GMAIL_PASSWORD", "ocwo vozn pskp copd")

if not GMAIL_PASSWORD or GMAIL_PASSWORD == "votre_mot_de_passe":
    st.error("⚠️ Configuration Gmail manquante. Vérifiez les variables d'environnement.")

def load_css():
    """Charge le CSS depuis le fichier externe"""
    try:
        # Chemin direct dans le même répertoire
        css_path = os.path.join(os.path.dirname(__file__), "style.css")
        
        if os.path.exists(css_path):
            with open(css_path, 'r', encoding='utf-8') as f:
                css_content = f.read()
            st.markdown(f'<style>{css_content}</style>', unsafe_allow_html=True)
        else:
            # Fallback CSS
            st.markdown("""
            <style>
                .main-header { color: #0074D9; text-align: center; }
                .stButton > button { background-color: #0074D9; color: white; }
            </style>
            """, unsafe_allow_html=True)
            st.warning(f"Fichier CSS non trouvé à: {css_path}")
            
    except Exception as e:
        st.error(f"Erreur lors du chargement du CSS: {e}")

def get_logo_path():
    """Retourne le chemin correct vers le logo"""
    possible_paths = [
        "Logo.PNG",
        "./Logo.PNG",
        "app/Logo.PNG",
        "./app/Logo.PNG",
        os.path.join(os.path.dirname(__file__), "Logo.PNG"),
        "images/Logo.PNG",
        "./images/Logo.PNG"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            return path
    return None

def get_logo_base64():
    """Retourne le logo encodé en base64 ou None si non trouvé"""
    try:
        logo_path = get_logo_path()
        if logo_path and os.path.exists(logo_path):
            with open(logo_path, "rb") as img_file:
                return base64.b64encode(img_file.read()).decode()
    except Exception:
        pass
    return None

def show_logo(container, width=240):
    """Affiche le logo avec gestion d'erreur robuste"""
    try:
        logo_b64 = get_logo_base64()
        if logo_b64:
            container.markdown(
                f'<img src="data:image/png;base64,{logo_b64}" width="{width}" style="display:block;margin:auto">',
                unsafe_allow_html=True
            )
        else:
            container.markdown(
                f'<div style="font-size: {width//3}px; color: var(--primary-color); text-align: center; margin: 20px 0;">🏛️</div>', 
                unsafe_allow_html=True
            )
            container.caption("Consular Services")
    except Exception as e:
        container.markdown(
            f'<div style="font-size: {width//3}px; color: var(--primary-color); text-align: center; margin: 20px 0;">📧</div>', 
            unsafe_allow_html=True
        )
        container.caption("Service Consulaire")

def check_authentication():
    """Vérifie si l'utilisateur est authentifié"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        show_login_page()
        return False
    return True

def show_login_page():
    """Affiche la page de connexion"""
    st.set_page_config(
        page_title="Connexion - Consular Services",
        page_icon="🔐",
        layout="centered"
    )
    
    # Charger le CSS unifié
    load_css()
    
    col_logo, col_form = st.columns([0.6, 1.2])
    
    with col_logo:
        show_logo(st, 240)

    with col_form:
        st.markdown("""
        <h3 class="login-title">Consular Services</h3>
        <p style="text-align: center; font-weight: bold; color: #495057; margin-top: -10px; margin-bottom: 30px;">
            Plateforme d'envoi de mails
        </p>
    """, unsafe_allow_html=True)
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
            
            col_submit, col_cancel = st.columns(2)
            with col_submit:
                submit_clicked = st.form_submit_button(
                    "Se connecter", 
                    use_container_width=True,
                    type="primary"
                )
            
            with col_cancel:
                cancel_clicked = st.form_submit_button(
                    "Annuler", 
                    use_container_width=True,
                    type="secondary"
                )
            
            if submit_clicked:
                if username == "Admin" and password == "Admin10":
                    st.session_state.authenticated = True
                    st.rerun()
                else:
                    st.markdown(
                        '<div class="login-error">Identifiants incorrects</div>', 
                        unsafe_allow_html=True
                    )

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

# ... (le début du code reste inchangé jusqu'ici)

def send_email_direct(to_email, subject, template_vars):
    """Envoie un email avec logo intégré (remplace l'icône 🏛️ par Logo.PNG)"""
    try:
        # 1. Préparation du message MIME
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"{template_vars.get('company_name', 'Services Consulaires')} <{GMAIL_USER}>"
        msg['To'] = to_email
        
        # Définir l'URL/CID du logo et la partie MIME correspondante
        logo_html_tag = '<div class="logo">🏛️</div>'  # Par défaut, utilise l'icône
        logo_attachment = None
        
        logo_path = get_logo_path()
        if logo_path:
            with open(logo_path, 'rb') as fp:
                logo_attachment = MIMEImage(fp.read(), _subtype='png')
                logo_attachment.add_header('Content-ID', '<logo_cid>')
                # Important: l'ID doit correspondre à ce qui est utilisé dans la balise <img>
                logo_html_tag = '<img src="cid:logo_cid" alt="Logo Consulaire" style="max-width: 80px; height: auto; margin-bottom: 10px; display: block; margin-left: auto; margin-right: auto;">'
        
        # 2. Construction du contenu HTML
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                /* Styles conservés pour la mise en page de l'e-mail */
                body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f4f4f4; }}
                .email-container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                .header {{ background: #0074D9; color: white; padding: 20px; text-align: center; }}
                /* Le style .logo est maintenant moins pertinent s'il s'agit d'une image */
                .header h1 {{ margin: 0; font-size: 22px; }}
                .content {{ padding: 30px; line-height: 1.6; color: #333; }}
                .info-box {{ background: #f8f9fa; border-left: 4px solid #0074D9; padding: 15px; margin: 20px 0; }}
                .signature {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; }}
                .sender-name {{ font-weight: bold; color: #0074D9; }}
                .footer {{ background: #f8f9fa; padding: 20px; text-align: center; color: #666; font-size: 12px; }}
                .message-content img {{ max-width: 100%; height: auto; }}
                .action-button a {{ 
                    display: inline-block; 
                    background-color: #0074D9; 
                    color: white; 
                    padding: 10px 20px; 
                    text-decoration: none; 
                    border-radius: 5px; 
                    margin-top: 15px;
                }}
            </style>
        </head>
        <body>
            <div class="email-container">
                <div class="header">
                    {logo_html_tag} <h1>{template_vars.get('company_name', 'Services Consulaires')}</h1>
                    <p><strong>{subject}</strong></p>
                </div>
                
                <div class="content">
                    <div style="font-size: 16px; margin-bottom: 20px;">
                        <strong>Bonjour {template_vars.get('recipient_name', '')},</strong>
                    </div>
                    
                    <div class="message-content">
                        {template_vars.get('message_content', '').replace(chr(10), '<br>')}
                    </div>
                    
                    {f'<div class="info-box"><strong>Informations importantes:</strong><br>{template_vars.get("additional_info", "").replace(chr(10), "<br>")}</div>' if template_vars.get('additional_info') else ''}
                    
                    {f"""
                    <div class="action-button" style="text-align: center;">
                        <a href="{template_vars.get('call_to_action_url', '#')}" target="_blank">
                            {template_vars.get('call_to_action_text', 'Aller à l\'action')}
                        </a>
                    </div>
                    """ if template_vars.get('call_to_action_url') and template_vars.get('call_to_action_text') else ''}

                    <div class="signature">
                        <p>Cordialement,</p>
                        <p class="sender-name">{template_vars.get('sender_name', 'Service Consulaire')}</p>
                        <p><strong>{template_vars.get('company_name', 'Services Consulaires')}</strong></p>
                        <p>Email: {template_vars.get('contact_email', 'consular.services.infos@gmail.com')}</p>
                        <p>Téléphone: {template_vars.get('contact_phone', '')}</p>
                        {f'<p>Département: {template_vars.get("department", "")}</p>' if template_vars.get('department') else ''}
                    </div>
                </div>
                
                <div class="footer">
                    <strong>{template_vars.get('company_name', 'Services Consulaires')}</strong><br>
                    {template_vars.get('company_address', '')}<br><br>
                    &copy; {datetime.now().year} {template_vars.get('company_name', 'Services Consulaires')}. Tous droits réservés.
                </div>
            </div>
        </body>
        </html>
        """

        # 3. Construction du contenu Texte (pour les clients sans HTML)
        text_content = f"""
SERVICES CONSULAIRES
{'=' * 20}

Objet: {subject}

Bonjour {template_vars.get('recipient_name', '')},

{template_vars.get('message_content', '')}

{f"INFORMATIONS IMPORTANTES:\n{template_vars.get('additional_info', '')}" if template_vars.get('additional_info') else ""}

{f"Action: {template_vars.get('call_to_action_text', 'Lien')}: {template_vars.get('call_to_action_url', '#')}" if template_vars.get('call_to_action_url') else ''}

Cordialement,
{template_vars.get('sender_name', 'Service Consulaire')}
{template_vars.get('company_name', 'Services Consulaires')}
Email: {template_vars.get('contact_email', 'consular.services.infos@gmail.com')}
Téléphone: {template_vars.get('contact_phone', '')}

{template_vars.get('company_address', '')}
        """

        # 4. Assemblage final et envoi
        msg.attach(MIMEText(text_content, 'plain'))
        # Ajout de la partie HTML
        html_part = MIMEMultipart('related')
        html_part.attach(MIMEText(html_content, 'html'))
        if logo_attachment:
            html_part.attach(logo_attachment) # Ajoute le logo comme image liée
        msg.attach(html_part)

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        return True, f"✅ Email envoyé avec succès à {to_email}"
        
    except Exception as e:
        return False, f"❌ Erreur lors de l'envoi de l'e-mail: {str(e)}"

# ... (le reste du code, y compris la fonction main_app, reste inchangé)

def main_app():
    """Interface principale après authentification"""
    st.set_page_config(
        page_title="Consular Services - Envoi d'Emails",
        page_icon="📧",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Charger le CSS unifié
    load_css()

    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.markdown('<div class="main-header">Consular Services - Plateforme d\'envoi d\'emails</div>', unsafe_allow_html=True)

    with st.sidebar:
        show_logo(st.sidebar, 200)
        
        st.markdown("---")
        st.subheader("Informations par défaut")
        
        default_company = st.text_input("Nom de l'entreprise", value="Services Consulaires")
        default_sender = st.text_input("Nom de l'expéditeur", value="Service Consulaire")
        default_contact_email = st.text_input("Email de contact", value="consular.services.infos@gmail.com")
        default_phone = st.text_input("Téléphone", value="+33 1 45 67 89 00")
        default_address = st.text_input("Adresse", value="123 Avenue des Diplomates, 75008 Paris, France")
        
        st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
        if st.button("Déconnexion", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📝 Composition", "👀 Prévisualisation", "📊 Historique"])

    with tab1:
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
            
            st.markdown("---")
            
            if st.button("Envoyer l'email", type="primary", use_container_width=True, disabled=not connection_success):
                if not all([to_email, recipient_name, subject, message_content]):
                    st.markdown('<div class="error-message">Veuillez remplir tous les champs obligatoires (*)</div>', unsafe_allow_html=True)
                else:
                    template_vars = {
                        'company_name': company_name,
                        'email_subject': subject,
                        'recipient_name': recipient_name,
                        'message_content': message_content,
                        'additional_info': additional_info,
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
            logo_b64 = get_logo_base64()
            
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
                <div style="background: linear-gradient(135deg, #0074D9 0%, #7FDBFF 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                    {f'<img src="data:image/png;base64,{logo_b64}" alt="Logo" style="max-width: 120px; margin-bottom: 15px;">' if logo_b64 else '<div style="font-size: 40px; margin-bottom: 15px;">🏛️</div>'}
                    <h1 style="margin: 0; font-size: 24px;">{preview_data['company_name']}</h1>
                    <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">{preview_data['subject']}</p>
                </div>
                
                <div style="padding: 30px; background: white; border-radius: 0 0 10px 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <p style="font-size: 16px; margin-bottom: 20px;"><strong> {preview_data['recipient_name']},</strong></p>
                    
                    <div style="font-size: 14px; line-height: 1.7; margin-bottom: 25px;">
                        {preview_data['message_content']}
                    </div>
                    
                    {f'<div style="background: #f8f9fa; border-left: 4px solid #0074D9; padding: 15px; margin: 15px 0; border-radius: 0 8px 8px 0;"><strong>Informations importantes:</strong><br>{preview_data.get("additional_info", "")}</div>' if preview_data.get('additional_info') else ''}
                    
                    {f'<div style="text-align: center; margin: 25px 0;"><a href="{preview_data["call_to_action_url"]}" style="background: linear-gradient(135deg, #0074D9 0%, #7FDBFF 100%); color: white; padding: 12px 30px; text-decoration: none; border-radius: 25px; display: inline-block;">{preview_data["call_to_action_text"]}</a></div>' if preview_data.get('call_to_action_url') and preview_data.get('call_to_action_text') else ''}
                    
                    <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #eaeaea;">
                        <p style="margin: 5px 0; color: #0074D9; font-weight: 600;">{preview_data['sender_name']}</p>
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
            emails_data = list(reversed(st.session_state.sent_emails))
            
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
                            st.success("✅ Envoyé")
                        else:
                            st.error("❌ Échec")
                    
                    if i < len(emails_data) - 1:
                        st.markdown("---")

    st.markdown("---")
    st.markdown(
        '<div style="text-align: center; color: #666; font-size: 14px;">'
        "Consular Services Email Platform • "
        "consular.services.infos@gmail.com • "
        f"© {datetime.now().year} Tous droits réservés"
        "</div>", 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    if check_authentication():
        main_app()


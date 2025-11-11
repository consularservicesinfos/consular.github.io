from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import jinja2
import os
from config import Config

app = Flask(__name__)
CORS(app)
app.config.from_object(Config)

# Configuration du template loader
template_loader = jinja2.FileSystemLoader('templates/')
template_env = jinja2.Environment(loader=template_loader)

def send_email(to_email, subject, template_vars):
    """
    Envoie un email via Gmail avec un template HTML personnalisable
    """
    try:
        # Charger et render le template
        template = template_env.get_template('email_template.html')
        html_content = template.render(**template_vars)
        
        # Création du message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = f"Consular Services <{app.config['GMAIL_USER']}>"
        msg['To'] = to_email
        
        # Version texte simple (fallback)
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
        
        # Attacher les versions texte et HTML
        msg.attach(MIMEText(text_content, 'plain'))
        msg.attach(MIMEText(html_content, 'html'))
        
        # Connexion au serveur Gmail
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(app.config['GMAIL_USER'], app.config['GMAIL_PASSWORD'])
        
        # Envoi de l'email
        server.send_message(msg)
        server.quit()
        
        return True, "Email envoyé avec succès"
        
    except Exception as e:
        return False, f"Erreur lors de l'envoi: {str(e)}"

@app.route('/api/send-email', methods=['POST'])
def send_email_api():
    """
    Endpoint API pour envoyer des emails personnalisés
    """
    try:
        data = request.get_json()
        
        # Validation des données requises
        required_fields = ['to_email', 'subject', 'recipient_name', 'message_content']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Champ manquant: {field}'
                }), 400
        
        # Variables pour le template avec valeurs par défaut
        template_vars = {
            'company_name': data.get('company_name', 'Consular Services'),
            'email_subject': data.get('subject', ''),
            'recipient_name': data.get('recipient_name', ''),
            'message_content': data.get('message_content', ''),
            'additional_info': data.get('additional_info', ''),
            'sender_name': data.get('sender_name', 'Service Consulaire'),
            'contact_email': data.get('contact_email', 'consular.services.infos@gmail.com'),
            'contact_phone': data.get('contact_phone', '+33 1 23 45 67 89'),
            'department': data.get('department', ''),
            'company_address': data.get('company_address', 'Paris, France'),
            'call_to_action_url': data.get('call_to_action_url', ''),
            'call_to_action_text': data.get('call_to_action_text', ''),
            'unsubscribe_url': data.get('unsubscribe_url', '#')
        }
        
        # Envoi de l'email
        success, message = send_email(
            data['to_email'],
            data['subject'],
            template_vars
        )
        
        return jsonify({
            'success': success,
            'message': message,
            'email_sent_to': data['to_email']
        }), 200 if success else 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur serveur: {str(e)}'
        }), 500

@app.route('/api/send-bulk-emails', methods=['POST'])
def send_bulk_emails():
    """
    Endpoint pour envoyer des emails en masse à plusieurs destinataires
    """
    try:
        data = request.get_json()
        
        required_fields = ['recipients', 'subject', 'message_content']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'Champ manquant: {field}'
                }), 400
        
        results = []
        for recipient in data['recipients']:
            template_vars = {
                'company_name': data.get('company_name', 'Consular Services'),
                'email_subject': data.get('subject', ''),
                'recipient_name': recipient.get('name', ''),
                'message_content': data.get('message_content', ''),
                'additional_info': data.get('additional_info', ''),
                'sender_name': data.get('sender_name', 'Service Consulaire'),
                'contact_email': data.get('contact_email', 'consular.services.infos@gmail.com'),
                'contact_phone': data.get('contact_phone', '+33 1 23 45 67 89'),
                'department': data.get('department', ''),
                'company_address': data.get('company_address', 'Paris, France'),
                'call_to_action_url': data.get('call_to_action_url', ''),
                'call_to_action_text': data.get('call_to_action_text', ''),
                'unsubscribe_url': data.get('unsubscribe_url', '#')
            }
            
            success, message = send_email(
                recipient['email'],
                data['subject'],
                template_vars
            )
            
            results.append({
                'email': recipient['email'],
                'success': success,
                'message': message
            })
        
        return jsonify({
            'success': True,
            'results': results,
            'total_sent': len([r for r in results if r['success']]),
            'total_failed': len([r for r in results if not r['success']])
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erreur serveur: {str(e)}'
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy', 
        'service': 'Consular Services Email API',
        'version': '1.0'
    })

@app.route('/api/template-variables', methods=['GET'])
def get_template_variables():
    """
    Retourne la liste des variables disponibles pour le template
    """
    variables = {
        'required_fields': [
            'to_email', 
            'subject', 
            'recipient_name', 
            'message_content'
        ],
        'optional_fields': [
            'company_name',
            'additional_info',
            'sender_name',
            'contact_email',
            'contact_phone',
            'department',
            'company_address',
            'call_to_action_url',
            'call_to_action_text',
            'unsubscribe_url'
        ],
        'default_values': {
            'company_name': 'Consular Services',
            'contact_email': 'consular.services.infos@gmail.com',
            'sender_name': 'Service Consulaire'
        }
    }
    return jsonify(variables)

if __name__ == '__main__':
    # Créer le dossier templates s'il n'existe pas
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
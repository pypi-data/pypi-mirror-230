# instadump

## Requisitos
1. Cuenta de IG business.
2. Crear app de tipo `business` en https://developers.facebook.com/apps
3. Crear un system user en https://business.facebook.com/settings/system-users
    - Linkear app y cuenta de IG
    - Generar access token (sin expiración) con los permisos:
        - instagram_basic
        - business_management
        - pages_show_list
        - instagram_manage_insights
        - pages_read_engagement
        - pages_read_user_content

## Uso
1. Exportar variables de entorno (ver ejemplo `.env.example`)
2. Agregar accounts en `config.yaml`
3. Crear virtualenv,

```bash
poetry shell
poetry install
```

4. Correr script,
```bash
poetry run instadump --help
```
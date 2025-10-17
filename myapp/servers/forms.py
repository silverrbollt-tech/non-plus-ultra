from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class JoinServerForm(FlaskForm):
    code = StringField(
        "Server Code",
        validators=[DataRequired(), Length(min=6, max=10)],
        render_kw={"placeholder": "Enter server code (e.g. ABC123)"}
    )
    submit = SubmitField("Join Server")

class CreateServerForm(FlaskForm):
    name = StringField(
        "Server Name",
        validators=[DataRequired(), Length(min=1, max=80)],
        render_kw={"placeholder": "Enter server name"}
    )
    description = TextAreaField(
        "Description (Optional)",
        validators=[Length(max=500)],
        render_kw={"placeholder": "Enter server description", "rows": 3}
    )
    submit = SubmitField("Create Server")

class CreateChannelForm(FlaskForm):
    name = StringField(
        "Channel Name",
        validators=[DataRequired(), Length(min=1, max=80)],
        render_kw={"placeholder": "Enter channel name"}
    )
    submit = SubmitField("Create Channel")
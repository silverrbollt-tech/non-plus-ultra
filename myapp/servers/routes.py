from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from myapp import db
from myapp.models import Server, Channel, Message, Membership, Invite
from myapp.utils.helpers import generate_join_code, generate_invite_code
from . import servers
from .forms import JoinServerForm, CreateServerForm, CreateChannelForm

@servers.route("/")
@login_required
def list_servers():
    my_servers = [m.server for m in current_user.servers]
    form = JoinServerForm()
    return render_template("servers/list.html", servers=my_servers, form=form)

@servers.route("/join", methods=["POST"])
@login_required
def join_by_code_inline():
    form = JoinServerForm()
    if form.validate_on_submit():
        server = Server.query.filter_by(join_code=form.code.data.upper()).first()
        if server:
            if not Membership.query.filter_by(user_id=current_user.id, server_id=server.id).first():
                db.session.add(Membership(user_id=current_user.id, server_id=server.id, role="member"))
                db.session.commit()
                flash(f"Joined {server.name}!", "success")
            return redirect(url_for("servers.view_server", server_id=server.id))
        flash("Invalid server code.", "danger")
    return redirect(url_for("servers.list_servers"))

@servers.route("/create", methods=["GET", "POST"])
@login_required
def create_server():
    form = CreateServerForm()
    if form.validate_on_submit():
        # Generate unique join code
        join_code = generate_join_code()
        while Server.query.filter_by(join_code=join_code).first():
            join_code = generate_join_code()
        
        server = Server(
            name=form.name.data,
            description=form.description.data,
            join_code=join_code,
            owner_id=current_user.id
        )
        db.session.add(server)
        db.session.flush()  # Get the server ID
        
        # Add owner as member
        db.session.add(Membership(user_id=current_user.id, server_id=server.id, role="owner"))
        
        # Create default general channel
        general_channel = Channel(name="general", server_id=server.id)
        db.session.add(general_channel)
        
        db.session.commit()
        flash(f"Server '{server.name}' created successfully!", "success")
        return redirect(url_for("servers.view_server", server_id=server.id))
    
    return render_template("servers/create.html", form=form)

@servers.route("/<int:server_id>")
@login_required
def view_server(server_id):
    server = Server.query.get_or_404(server_id)
    
    # Check if user is a member
    membership = Membership.query.filter_by(user_id=current_user.id, server_id=server_id).first()
    if not membership:
        flash("You are not a member of this server.", "danger")
        return redirect(url_for("servers.list_servers"))
    
    channels = server.channels
    members = [m.user for m in server.members]
    
    return render_template("servers/view.html", server=server, channels=channels, members=members)

@servers.route("/<int:server_id>/channel/<int:channel_id>")
@login_required
def view_channel(server_id, channel_id):
    server = Server.query.get_or_404(server_id)
    channel = Channel.query.get_or_404(channel_id)
    
    # Check if user is a member
    membership = Membership.query.filter_by(user_id=current_user.id, server_id=server_id).first()
    if not membership:
        flash("You are not a member of this server.", "danger")
        return redirect(url_for("servers.list_servers"))
    
    # Get recent messages
    messages = Message.query.filter_by(channel_id=channel_id).order_by(Message.created_at.desc()).limit(50).all()
    messages.reverse()  # Show oldest first
    
    return render_template("servers/channel.html", server=server, channel=channel, messages=messages)

@servers.route("/<int:server_id>/create_channel", methods=["POST"])
@login_required
def create_channel(server_id):
    server = Server.query.get_or_404(server_id)
    
    # Check if user is owner or admin
    membership = Membership.query.filter_by(user_id=current_user.id, server_id=server_id).first()
    if not membership or membership.role not in ['owner', 'admin']:
        flash("You don't have permission to create channels.", "danger")
        return redirect(url_for("servers.view_server", server_id=server_id))
    
    form = CreateChannelForm()
    if form.validate_on_submit():
        channel = Channel(
            name=form.name.data,
            server_id=server_id
        )
        db.session.add(channel)
        db.session.commit()
        flash(f"Channel '{channel.name}' created successfully!", "success")
    
    return redirect(url_for("servers.view_server", server_id=server_id))

@servers.route("/<int:server_id>/invite")
@login_required
def create_invite(server_id):
    server = Server.query.get_or_404(server_id)
    
    # Check if user is a member
    membership = Membership.query.filter_by(user_id=current_user.id, server_id=server_id).first()
    if not membership:
        flash("You are not a member of this server.", "danger")
        return redirect(url_for("servers.list_servers"))
    
    # Generate invite code
    invite_code = generate_invite_code()
    while Invite.query.filter_by(code=invite_code).first():
        invite_code = generate_invite_code()
    
    invite = Invite(
        code=invite_code,
        server_id=server_id,
        created_by=current_user.id
    )
    db.session.add(invite)
    db.session.commit()
    
    invite_url = f"{request.url_root}servers/join/{invite_code}"
    return jsonify({"invite_url": invite_url, "code": invite_code})

@servers.route("/join/<invite_code>")
@login_required
def join_by_invite(invite_code):
    invite = Invite.query.filter_by(code=invite_code).first()
    if not invite:
        flash("Invalid invite code.", "danger")
        return redirect(url_for("servers.list_servers"))
    
    # Check if user is already a member
    if Membership.query.filter_by(user_id=current_user.id, server_id=invite.server_id).first():
        flash("You are already a member of this server.", "info")
        return redirect(url_for("servers.view_server", server_id=invite.server_id))
    
    # Add user to server
    db.session.add(Membership(user_id=current_user.id, server_id=invite.server_id, role="member"))
    
    # Update invite usage
    invite.uses += 1
    db.session.commit()
    
    flash(f"Joined {invite.server.name}!", "success")
    return redirect(url_for("servers.view_server", server_id=invite.server_id))
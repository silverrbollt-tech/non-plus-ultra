import uuid
import secrets
import string, random
from datetime import datetime, timedelta
from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    abort,
    request,
    jsonify,
)
from flask_login import login_required, current_user
from auth_app.extensions import socketio, db
from auth_app.forms import CreateServerForm, CreateChannelForm, JoinServerForm
from auth_app.models import Server, ServerMember, Channel, Message, Invite
from flask_socketio import emit, join_room, leave_room


# ==============================
# Blueprint
# ==============================
servers = Blueprint("servers", __name__, template_folder="templates")
print("📌 Servers blueprint registered!")


# ==============================
# HELPERS
# ==============================
def generate_invite_code(length=12):
    """Generate a secure, URL-safe invite code."""
    return secrets.token_urlsafe(length)[:length]


def generate_server_code(length=6):
    """Generate a classroom-style server join code like ABC123."""
    chars = string.ascii_uppercase + string.digits
    return ''.join(random.choices(chars, k=length))


def require_admin_or_owner(server, user):
    """Ensure user has admin/owner privileges on a server."""
    membership = ServerMember.query.filter_by(
        user_id=user.id, server_id=server.id
    ).first()
    if not membership or membership.role not in ["owner", "admin"]:
        abort(403)
    return membership


# ==============================
# SERVER MANAGEMENT
# ==============================
@servers.route("/")
@login_required
def list_servers():
    """List servers where the current user is a member and show join form."""
    my_servers = [membership.server for membership in current_user.servers]
    form = JoinServerForm()
    return render_template("servers/list.html", servers=my_servers, form=form)


@servers.route("/create", methods=["GET", "POST"])
@login_required
def create_server():
    """Create a new server."""
    form = CreateServerForm()
    if form.validate_on_submit():
        server = Server(
            name=form.name.data,
            description=form.description.data,
            owner=current_user,
            join_code=generate_server_code()  # Generate join code on creation
        )
        db.session.add(server)
        db.session.flush()  # Ensure server.id is available
        membership = ServerMember(user=current_user, server=server, role="owner")
        db.session.add(membership)
        db.session.commit()
        flash("✅ Server created successfully!", "success")
        return redirect(url_for("servers.list_servers"))
    return render_template("servers/create.html", form=form)


@servers.route("/<int:server_id>")
@login_required
def view_server(server_id):
    """View a specific server with its channels."""
    server = Server.query.get_or_404(server_id)
    members = [{'user_id': m.user_id, 'username': m.user.username, 'is_online': m.user.is_online} for m in server.members]
    membership = ServerMember.query.filter_by(
        user_id=current_user.id, server_id=server.id
    ).first()
    if not membership:
        abort(403)
    form = JoinServerForm()  # Added for join-by-code form
    return render_template(
        "servers/view.html",
        server=server,
        membership=membership,
        form=form,
        members=members
    )


@servers.route("/<int:server_id>/reset_code", methods=["POST"])
@login_required
def reset_join_code(server_id):
    """Reset the join code for a server (admin/owner only)."""
    server = Server.query.get_or_404(server_id)
    membership = ServerMember.query.filter_by(
        user_id=current_user.id, server_id=server.id
    ).first()
    if not membership or membership.role not in ["owner", "admin"]:
        abort(403)
    server.join_code = generate_server_code()
    db.session.commit()
    flash("🔑 Server join code has been reset!", "success")
    return redirect(url_for("servers.view_server", server_id=server.id))


# ==============================
# CHANNEL MANAGEMENT
# ==============================
@socketio.on("join_server")
def handle_join_server(data):
    server_id = data.get("server_id")
    room = f"server_{server_id}"
    join_room(room)
    server = Server.query.get(server_id)
    members = [
        {"username": m.user.username, "role": m.role}
        for m in server.members
    ]
    emit("update_members", members, to=room)


@socketio.on("leave_server")
def handle_leave_server(data):
    server_id = data.get("server_id")
    room = f"server_{server_id}"
    leave_room(room)
    server = Server.query.get(server_id)
    members = [
        {"username": m.user.username, "role": m.role}
        for m in server.members
    ]
    emit("update_members", members, to=room)


@servers.route("/<int:server_id>/channels/create", methods=["GET", "POST"])
@login_required
def create_channel(server_id):
    """Create a channel inside a server (owner/admin only)."""
    server = Server.query.get_or_404(server_id)
    require_admin_or_owner(server, current_user)
    form = CreateChannelForm()
    if form.validate_on_submit():
        channel = Channel(name=form.name.data, server=server)
        db.session.add(channel)
        db.session.commit()
        flash(f"✅ Channel '{form.name.data}' created!", "success")
        return redirect(url_for("servers.view_server", server_id=server.id))
    return render_template("servers/create_channel.html", form=form, server=server)


@servers.route("/<int:server_id>/channels/<int:channel_id>")
@login_required
def view_channel(server_id, channel_id):
    """View messages in a channel."""
    server = Server.query.get_or_404(server_id)
    channel = Channel.query.filter_by(
        id=channel_id, server_id=server.id
    ).first_or_404()
    membership = ServerMember.query.filter_by(
        user_id=current_user.id, server_id=server.id
    ).first()
    if not membership:
        abort(403)
    messages = (
        Message.query.filter_by(channel_id=channel.id)
        .order_by(Message.timestamp.asc())
        .limit(50)
        .all()
    )
    form = JoinServerForm()  # Added for join-by-code form
    return render_template(
        "servers/view_channel.html",
        server=server,
        channel=channel,
        messages=messages,
        membership=membership,
        form=form,
        current_channel=channel
    )


# ==============================
# MESSAGES
# ==============================
@servers.route("/<int:server_id>/channels/<int:channel_id>/send", methods=["POST"])
@login_required
def send_message(server_id, channel_id):
    """Save a message in the DB (for API/AJAX calls)."""
    server = Server.query.get_or_404(server_id)
    channel = Channel.query.filter_by(
        id=channel_id, server_id=server.id
    ).first_or_404()
    membership = ServerMember.query.filter_by(
        user_id=current_user.id, server_id=server.id
    ).first()
    if not membership:
        abort(403)
    data = request.get_json()
    content = (data.get("content") or "").strip()
    if not content:
        return jsonify({"error": "Empty message"}), 400
    msg = Message(content=content, user=current_user, channel=channel)
    db.session.add(msg)
    db.session.commit()
    
    # Emit the message to all clients in the channel room
    socketio.emit("message", {
        "username": current_user.username,
        "content": content,
        "timestamp": msg.timestamp.strftime('%Y-%m-%d %H:%M')
    }, room=f"channel_{channel_id}")
    
    return jsonify({"success": True, "message": content})


# ==============================
# SOCKET.IO HANDLERS
# ==============================
@socketio.on("join")
def handle_join(data):
    """Handle joining a room (channel)."""
    room = data.get("room")
    if room:
        join_room(room)
        print(f"User {current_user.username if current_user.is_authenticated else 'Anonymous'} joined room {room}")


@socketio.on("send_message")
def handle_send_message(data):
    """Handle sending a message via Socket.IO."""
    if not current_user.is_authenticated:
        emit("error", {"message": "Not authenticated"})
        return
    
    room = data.get("room")
    content = data.get("content", "").strip()
    
    if not content:
        emit("error", {"message": "Empty message"})
        return
    
    # Extract channel_id from room name (format: channel_123)
    if room and room.startswith("channel_"):
        try:
            channel_id = int(room.split("_")[1])
            channel = Channel.query.get(channel_id)
            if not channel:
                emit("error", {"message": "Channel not found"})
                return
            
            # Check if user is member of the server
            membership = ServerMember.query.filter_by(
                user_id=current_user.id, server_id=channel.server_id
            ).first()
            if not membership:
                emit("error", {"message": "Not a member of this server"})
                return
            
            # Create and save message
            msg = Message(content=content, user=current_user, channel=channel)
            db.session.add(msg)
            db.session.commit()
            
            # Emit message to all clients in the room
            emit("message", {
                "username": current_user.username,
                "content": content,
                "timestamp": msg.timestamp.strftime('%Y-%m-%d %H:%M')
            }, room=room)
            
        except (ValueError, IndexError):
            emit("error", {"message": "Invalid room format"})
    else:
        emit("error", {"message": "Invalid room"})

# ==============================
# INVITES (Discord-style)
# ==============================
@servers.route("/server/<int:server_id>/invite/create", methods=["GET", "POST"])
@login_required
def create_invite(server_id):
    """Create a new invite link (admin/owner only)."""
    server = Server.query.get_or_404(server_id)
    require_admin_or_owner(server, current_user)
    code = uuid.uuid4().hex[:8]
    invite = Invite(
        code=code,
        server=server,
        creator=current_user,
        max_uses=0,
        expires_at=datetime.utcnow() + timedelta(days=1),
    )
    db.session.add(invite)
    db.session.commit()
    flash("✅ Invite created!", "success")
    return render_template("servers/invite.html", server=server, invite=invite)


@servers.route("/invite/<code>", methods=["GET", "POST"])
@login_required
def join_server(code):
    """Landing page for invite links."""
    invite = Invite.query.filter_by(code=code).first_or_404()
    if not invite.is_valid:
        return render_template(
            "servers/invite_landing.html", invite=invite, server=invite.server
        )
    server = invite.server
    membership = ServerMember.query.filter_by(
        user_id=current_user.id, server_id=server.id
    ).first()
    if membership:
        flash("⚠️ You're already a member of this server.", "info")
        return redirect(url_for("servers.view_server", server_id=server.id))
    if request.method == "POST":
        membership = ServerMember(user_id=current_user.id, server_id=server.id, role="member")
        db.session.add(membership)
        invite.uses += 1
        db.session.commit()
        flash(f"🎉 You joined {server.name}!", "success")
        return redirect(url_for("servers.view_server", server_id=server.id))
    return render_template("servers/invite_landing.html", invite=invite, server=server)


@servers.route("/invite/<int:invite_id>/revoke", methods=["POST"])
@login_required
def revoke_invite(invite_id):
    """Revoke an invite (admin/owner only)."""
    invite = Invite.query.get_or_404(invite_id)
    require_admin_or_owner(invite.server, current_user)
    invite.revoked = True
    db.session.commit()
    flash("🚫 Invite revoked.", "warning")
    return redirect(url_for("servers.view_server", server_id=invite.server_id))


# ==============================
# JOIN BY CODE (Classroom-style)
# ==============================
@servers.route("/join", methods=["GET", "POST"])
@login_required
def join_by_code():
    """Join a server using a classroom-style join code."""
    form = JoinServerForm()
    if form.validate_on_submit():
        code = form.code.data.strip().upper()
        server = Server.query.filter_by(join_code=code).first()
        if not server:
            flash("❌ Invalid server code.", "danger")
            return redirect(url_for("servers.join_by_code"))
        membership = ServerMember.query.filter_by(
            user_id=current_user.id, server_id=server.id
        ).first()
        if membership:
            flash("⚠️ You are already a member of this server.", "info")
            return redirect(url_for("servers.view_server", server_id=server.id))
        new_member = ServerMember(user_id=current_user.id, server_id=server.id, role="member")
        db.session.add(new_member)
        db.session.commit()
        flash(f"🎉 Successfully joined {server.name}!", "success")
        return redirect(url_for("servers.view_server", server_id=server.id))
    return render_template("servers/join.html", form=form)


@servers.route("/join-inline", methods=["POST"])
@login_required
def join_by_code_inline():
    """Join a server using a code, directly from any page."""
    form = JoinServerForm()
    if form.validate_on_submit():
        code = form.code.data.strip().upper()
        server = Server.query.filter_by(join_code=code).first()
        if not server:
            flash("❌ Invalid server code.", "danger")
            return redirect(request.referrer or url_for("servers.list_servers"))
        membership = ServerMember.query.filter_by(
            user_id=current_user.id, server_id=server.id
        ).first()
        if membership:
            flash("⚠️ You are already a member of this server.", "info")
            return redirect(url_for("servers.view_server", server_id=server.id))
        new_member = ServerMember(user_id=current_user.id, server_id=server.id, role="member")
        db.session.add(new_member)
        db.session.commit()
        flash(f"🎉 Successfully joined {server.name}!", "success")
        return redirect(url_for("servers.view_server", server_id=server.id))
    flash("❌ Invalid input. Please check the server code.", "danger")
    return redirect(request.referrer or url_for("servers.list_servers"))
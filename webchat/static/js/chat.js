function chatInit (scheme, locale, rooms_num) {
    var $rooms_list = $('#rooms_list');
    var $rooms_list_ul = $('#rooms_list_ul');
    
    var $chat_text = $('#chat_text');
    var $chat_content = $('#chat_content');
    var $msg_text = $('#msg_text');
    var $nick_name_input = $('#nick_name_input');
    var $send_btn = $('#send_button');
    var $change_btn = $('#change_room');
    
    var current_room_id = 0;
    var default_nick_name = "";
    var nick_name = "";
    var password = "";
    var target_room_id = 0;
    
    var local = window.location.host;
    var uri_scheme = (scheme == 'https')? 'wss://' : 'ws://';
    var uri = uri_scheme + local + '/websocket/chat/0';
    // console.log('Uri: ' + uri)
    
    var WebSocket = window.WebSocket || window.MozWebSocket;
    if (WebSocket) {
        try {
            var socket = new WebSocket(uri);
        } catch (e) {}
    }
    
    $chat_text.val("");
    $msg_text.val("");
    
    
    if (socket) {
        socket.onopen = function() {
            // console.log("websocket onopen");
            $send_btn.bind("click", sendMessage);
            $change_btn.bind("click", changeRoom);
            $msg_text.keydown(function(e) {
                if (e.ctrlKey && e.keyCode == 13) {
                    sendMessage();
                }
            });
        }
        
        socket.onmessage = function(msg) {
            // console.log("websocket onmessage");
            var data = JSON.parse(msg.data);
            // console.log(data);
            if (data.cmd && data.cmd == "init_rooms_list" && data.rooms_list) {
                data.rooms_list.forEach(function (value, index, array_rooms) {
                    $rooms_list_ul.append(
                        '<a id="a_' + value.room_id + '" class="rooms_list_item list-group-item">' + 
                            '<p class="col-md-12 room_item_title">' + 
                                '<span id="room_num_badge" class="badge">' + "Room&nbsp" + 
                                intToString(value.room_id, "0", 3) + '</span>&nbsp' +
                            '</p>' +
                            '<p class="room_item_status">' + 
                                '<span class="pull-left">' + "Current Members:&nbsp" + 
                                intToString(value.current_members, "", 4) + '</span>&nbsp;' + 
                            '</p>' + 
                        '</a>'
                    );
                    initRoomClick(value.room_id);
                });
            }
            
            if (data.cmd && data.cmd == "refresh_rooms_list" && data.rooms_list) {
                data.rooms_list.forEach(function (value, index, array_rooms) {
                    $rooms_list_ul.find("a#a_" + value.room_id + ">p.room_item_title")
                                  .html('<span id="room_num_badge" class="badge">' + 
                                        "Room&nbsp" + intToString(value.room_id, "0", 3) + 
                                        '</span>&nbsp');
                    $rooms_list_ul.find("a#a_" + value.room_id + ">p.room_item_status")
                                  .html('<span class="pull-left">' + "Current Members:&nbsp" + 
                                        intToString(value.current_members, "", 4) + 
                                        '</span>&nbsp;');
                });
            }
            
            if (data.cmd && data.cmd == "new_msg") {
                if (data.nick_name && data.msg && data.date_time && data.default_nick_name) {
                    var msg_nick_name = Base64.decode(data.default_nick_name);
                    if (msg_nick_name != default_nick_name) {
                        var msg = Utf8.decode(Tea.strDecrypt(data.msg, password));
                        $chat_content.append('<div id="chat_item" class="list-group-item col-xs-12">' + 
                                                '<div id="chat_in_item" class="col-xs-9">' + 
                                                    '<span id="nick_name">' +
                                                        '<span id="chat_item_name" class="badge">' +
                                                            Utf8.decode(Base64.decode(data.nick_name)) + 
                                                        '</span>' +
                                                        " " + data.date_time + " " + 
                                                    '</span><br/>' +
                                                    '<span id="chat_item_text" class="col-xs-12">' +
                                                    msg + 
                                                    '</span>' + 
                                                '</div>' + 
                                            '</div>');
                        notify("WebChat Message", msg);
                    } else {
                        $chat_content.append('<div id="chat_item" class="list-group-item col-xs-12">' + 
                                                '<div id="chat_in_self" class="pull-right col-xs-9">' + 
                                                    '<span id="nick_name">' +
                                                        '<span id="chat_item_name" class="badge">' +
                                                            Utf8.decode(Base64.decode(data.nick_name)) + 
                                                        '</span>' +
                                                        " " + data.date_time + " " + 
                                                    '</span><br/>' +
                                                    '<span id="chat_item_text" class="col-xs-12">' +
                                                    Utf8.decode(Tea.strDecrypt(data.msg, password)) + 
                                                    '</span>' + 
                                                '</div>' + 
                                            '</div>');
                    }
                    
                } else {
                    $chat_content.append('<div id="chat_system" class="list-group-item col-xs-12">' + 
                                            '<span id="system">' + Base64.decode(data.msg) + 
                                            '</span>' + 
                                         '</div>');
                }
                
                $chat_text.scrollTop(chat_text.scrollHeight);
            }
            
            if (data.password) {
                password = data.password;
            }
            
            if (data.cmd && data.cmd == "change_rooms_list" && data.room_id) {
                current_room_id = data.room_id;
            }
            
            if (data.default_nick_name && data.cmd == "init_rooms_list") {
                default_nick_name = Utf8.decode(Base64.decode(data.default_nick_name));
                if (nick_name == "") {
                    nick_name = default_nick_name;
                }
                if ($nick_name_input.val().trim() == "") {
                    $nick_name_input.val(nick_name);
                }
            }
            
            // console.log("default_nick_name: " + default_nick_name);
        }
        
        socket.onclose = function() {
            // console.log("websocket onclose");
            $msg_text.css({'background-color' : '#CC0000'});
            $msg_text.val("Sorry, you are offline, please refresh this page!");
        }
    }
    
    function sendMessage() {
        // console.log("send msg: " + current_room_id);
        var data = {};
        data['cmd'] = "send_msg";
        var nick_name_tmp = $nick_name_input.val();
        if (nick_name_tmp.trim() != "") {
            data['nick_name'] = Base64.encode(Utf8.encode(nick_name_tmp));
        } else {
            data['nick_name'] = Base64.encode(Utf8.encode(default_nick_name));
            $nick_name_input.val(default_nick_name);
        }
        data['default_nick_name'] = Base64.encode(default_nick_name);
        data['room_id'] = current_room_id.toString();
        data['msg'] = Tea.strEncrypt(Utf8.encode(escapeHtml($msg_text.val())), password);
        if ($msg_text.val() != "" && current_room_id != 0) {
            socket.send(JSON.stringify(data));
            $msg_text.val("");
        } else if ($msg_text.val() == "" && current_room_id != 0) {
            $("#empty_message_modal").modal('show');
        } else {
            $("#first_select_modal").modal('show');
        }
    }
    
    function initRoomClick(room_id) {
        $('a#a_' + room_id).bind("click", function () {
            target_room_id = room_id;
            if (current_room_id != null && current_room_id != 0) {
                $("#change_room_modal").modal('show');
            } else {
                changeRoom();
            }
        });
    }
    
    function changeRoom() {
        var data = {};
        data['cmd'] = "change_room";
        data['room_id'] = target_room_id.toString();
        // console.log("click old_id: " + current_room_id);
        if (current_room_id != null && current_room_id != 0)
            $('a#a_' + current_room_id).attr("class","rooms_list_item list-group-item");
        current_room_id = target_room_id;
        // console.log("click new_id: " + current_room_id);
        $('a#a_' + current_room_id).attr("class","rooms_list_item list-group-item active");
        socket.send(JSON.stringify(data));
        $chat_content.empty();
    }

    function notify(title, msg) {
        if (!("Notification" in window)) {
            alert("This browser does not support desktop notification");
        } else if (Notification.permission === "granted") {
            // If it's okay let's create a notification
            var notification = new Notification(title, {"body": msg});
        } else if (Notification.permission !== 'denied') {
            Notification.requestPermission(function (permission) {
                if (permission === "granted") {
                    var notification = new Notification(title, {"body": msg});
                }
            });
        }
    }
    
    var entityMap = {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': '&quot;',
            "'": '&#39;',
            "/": '&#x2F;',
            "\n":'<br/>',
            " ": '&nbsp;'
        };

    function escapeHtml(string) {
        return String(string).replace(/[&<>"'\/\n ]/g, function (s) {
            return entityMap[s];
        });
    }
    
    function intToString(i, s, w) {
        var r = "";
        var i_s = i.toString();
        if (i_s.length < w) {
            for (var j = 0; j < (w - i_s.length); j++) {
                r += s;
            }
        }
        r += i_s;
        return r;
    }
    
}


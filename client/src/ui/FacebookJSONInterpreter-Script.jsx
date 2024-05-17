//            buddha please make this work
//                       _oo0oo_
//                      o8888888o
//                      88" . "88
//                      (| -_- |)
//                      0\  =  /0
//                    ___/`---'\___
//                  .' \\|     |// '.
//                 / \\|||  :  |||// \
//                / _||||| -:- |||||- \
//               |   | \\\  -  /// |   |
//               | \_|  ''\---/''  |_/ |
//               \  .-\__  '-'  ___/-. /
//             ___'. .'  /--.--\  `. .'___
//          ."" '<  `.___\_<|>_/___.' >' "".
//         | | :  `- \`.;`\ _ /`;.`/ - ` : | |
//         \  \ `_.   \_ __\ /__ _/   .-` /  /
//     =====`-.____`.___ \_____/___.-`___.-'=====
//                       `=---='


import React from 'react';
const message1 = require('../tests/message_1.json');
const message2 = require('../tests/message_2.json');
const message3 = require('../tests/message_3.json');
import './main.css';


const dateOptions = {
    weekday: 'short', year: 'numeric', month: 'short', day: 'numeric',
    hour: '2-digit', minute: '2-digit', second: '2-digit',
};

// Function: link api to client, then do ui and shits
function FacebookJSONInterpreterScript() {
    // step 1: read the fucking jsonfile (HARDCODED TO 3)
    const messagesFull = message1['messages'].concat(
        message2['messages'], message3['messages']);
    messagesFull.reverse();
    // messagesFull = messagesFull.slice(5000, 10000);
    // step 2: interpret the messages
    return (
        <div style={{margin: '2em'}}>
            {messagesFull.map(function(message, index) {
                return <MessageBubble message={message} index={index}/>;
            })}
        </div>
    );
}
function MessageBubble({message, index}) {
    const date = new Date(message['timestamp_ms']);
    let bumped = '';
    if (message['bumped_message_metadata']) {
        bumped = 'Bumped by ';
    }
    if (message['sticker']) {
        const name = message['sticker']['uri'].split('/').slice(-1);
        return (
            <div>
                <p className='senderName'>{bumped}{message['sender_name']}: {
                    date.toLocaleString('en-US', dateOptions)}</p>
                <img className='stickers' src={'./static/stickers/' + name}/>
            </div>
        );
    } else if (message['photos']) {
        const name = message['photos'];
        return (
            <div>
                <p className='senderName'>{bumped}{message['sender_name']}: {
                    date.toLocaleString('en-US', dateOptions)}</p>
                {name.map((img) => {
                    return <img className='photos' src={'./static/photos/' + img['uri'].split('/').slice(-1)}/>;
                })}
            </div>
        );
    } else if (message['is_unsent']) {
        return (
            <div>
                <p className='senderName'>{bumped}{message['sender_name']}: {
                    date.toLocaleString('en-US', dateOptions)}</p>
                <div className='contentContainerUnsent'>
                    <p>{message['sender_name']} unsent a message.</p>
                </div>
            </div>
        );
    } else if (message['videos']) {
        const name = message['videos'];
        return (
            <div>
                <p className='senderName'>{bumped}{message['sender_name']}: {
                    date.toLocaleString('en-US', dateOptions)}</p>
                {name.map((img) => {
                    return (
                        <video height="200" controls>
                            <source src={'./static/videos/' + img['uri'].split('/').slice(-1)} type="video/mp4"/>
                        </video>
                    );
                })}
            </div>
        );
    } else if (message['audio_files']) {
        const name = message['audio_files'];
        return (
            <div>
                <p className='senderName'>{bumped}{message['sender_name']}: {
                    date.toLocaleString('en-US', dateOptions)}</p>
                {name.map((img) => {
                    return (
                        <audio height="200" controls>
                            <source src={'./static/audio/' + img['uri'].split('/').slice(-1)[0].split('.')[0] + '.mp3'} type="audio/mpeg"/>
                        </audio>
                    );
                })}
            </div>
        );
    } else if (message['gifs']) {
        const name = message['gifs'];
        return (
            <div>
                <p className='senderName'>{bumped}{message['sender_name']}: {
                    date.toLocaleString('en-US', dateOptions)}</p>
                {name.map((img) => {
                    return <img className='photos' src={'./static/gifs/' + img['uri'].split('/').slice(-1)}/>;
                })}
            </div>
        );
    } else if (message['files']) {
        const name = message['files'];
        return (
            <div>
                <p className='senderName'>{bumped}{message['sender_name']}: {
                    date.toLocaleString('en-US', dateOptions)}</p>
                {name.map((img) => {
                    return <a href={'./static/files/' + img['uri'].split('/').slice(-1)}>{img['uri'].split('/').slice(-1)[0]}</a>;
                })}
            </div>
        );
    } else if (!message['content']) {
        return;
    } else if (message['content'].search(/(^.+ reacted .+ to your message)|(^This poll is no longer available$)|(^Reacted .+ to your message$)/g) != -1) {
        return;
    } else {
        return (
            <div>
                <p className='senderName'>{bumped}{message['sender_name']}: {
                    date.toLocaleString('en-US', dateOptions)}</p>
                <div className='contentContainerText'>
                    <p className='contentText'>{message['content']}</p>
                </div>
            </div>
        );
    }
}

export default FacebookJSONInterpreterScript;

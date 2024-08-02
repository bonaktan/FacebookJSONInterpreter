import React, {useContext, useState, useEffect} from "react"
import { useLoaderData } from "react-router-dom"
import GlobalVariables from "../../globals/globalVariables"

export default function Conversation() {
    const {chatId} = useLoaderData()
    const Globals = useContext(GlobalVariables)
    const [data, setData] = useState({'messages': []})
    const [inProgress, setInProgress] = useState(true)
    const api = Globals.API
    useEffect(() => {
        api.post('', {'requestType': 'loadConversation', 'chatId': chatId}).then((respo) => {
            setData(respo.data['data'])
        })
        setInProgress(false)
    }, [api, setData, chatId])
    
    return (
        <>
            {inProgress ?
                <p>Please Wait.</p> :
                <>
                    {data['messages'].toReversed().map((chat, index) => { // need the emergency engine
                        return <MessageBubble message={chat} key={index}/>
                    })}
                </>}
        </>
    )
}

const dateOptions = {
    weekday: 'short', year: 'numeric', month: 'short', day: 'numeric',
    hour: '2-digit', minute: '2-digit', second: '2-digit',
};
function MessageBubble({message}) {
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
                <img className='stickers' src={'http://127.0.0.1:42069/static/' + name}/>
            </div>
        );
    } else if (message['photos']) {
        const name = message['photos'];
        return (
            <div>
                <p className='senderName'>{bumped}{message['sender_name']}: {
                    date.toLocaleString('en-US', dateOptions)}</p>
                {name.map((img, index) => {
                    return <img key={index} className='photos' src={'http://127.0.0.1:42069/static/' + img['uri']}/>;
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
                {name.map((img, index) => {
                    return (
                        <video key={index} height="200" controls>
                            <source src={'http://127.0.0.1:42069/static/' + img['uri']} type="video/mp4"/>
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
                {name.map((img, index) => {
                    return (
                        <audio key={index} height="200" controls>
                            <source src={'http://127.0.0.1:42069/static/' + img['uri']} type="audio/mpeg"/>
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
                {name.map((img, index) => {
                    return <img key={index} className='photos' src={'http://127.0.0.1:42069/static/' + img['uri']}/>;
                })}
            </div>
        );
    } else if (message['files']) {
        const name = message['files'];
        return (
            <div>
                <p className='senderName'>{bumped}{message['sender_name']}: {
                    date.toLocaleString('en-US', dateOptions)}</p>
                {name.map((img, index) => {
                    return <a key={index} href={'http://127.0.0.1:42069/static/' + img['uri']}>{img['uri'].split('/').slice(-1)[0]}</a>;
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
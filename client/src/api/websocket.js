/* eslint-disable require-jsdoc */
import {useEffect, useState, useRef} from 'react';

const usePythonSocketBare = () => {
    const [ready, setReady] = useState(false);
    const socket = useRef(null);
    useEffect(() => {
        const _socket = new WebSocket('ws://127.0.0.1:42069/websocket');
        _socket.onopen = () => {
            setReady(true);
            _socket.send('AAAAAAAAAAAAAAAAAAAAAAAA  - miku and the choir');
        };
        _socket.onmessage = (event) => console.log(event);
        _socket.onclose = () => setReady(false);
        socket.current = _socket;
        return () => {
            setReady(false);
            _socket.close();
        };
    }, []);
    console.log(ready, socket);
    return {ready, socket, send: socket.current?.send.bind(socket.current)};
};

export default usePythonSocketBare;

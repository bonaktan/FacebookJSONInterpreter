import {useEffect, useState} from "react";


export default function useAPI() {
    const [requestData, sendRequest] = useState({});
    const [returnData, setData] = useState({})
    const [inProgress, setInProgress] = useState(0)
    useEffect(() => {
        setInProgress(1)
        const request = {
            method: 'POST',
            body: JSON.stringify(requestData)
        }
        console.log(request)
        async function reqFetch() {
            await fetch('http://localhost:42069/api', request)
                .then((res) => {return res.json();})
                .then((data) => {
                    setData(data);
                });
        }
        reqFetch()
    },[requestData]);
    useEffect(() => {setInProgress(0)}, [returnData])
    return {sendRequest, returnData, inProgress, requestData}
}

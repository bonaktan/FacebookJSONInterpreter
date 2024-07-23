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
        fetch('http://localhost:42069/api', request)
            .then((res) => {return res.json();})
            .then((data) => {
                setData(data);
            });
        setInProgress(0)
    },[requestData]);
    return {sendRequest, returnData, inProgress, requestData}
}

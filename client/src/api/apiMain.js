import {useEffect, useState} from "react";


export default function useAPI() {
    const [requestData, setRequestData] = useState({});
    const [returnData, setReturnData] = useState({})
    const [inProgress, setInProgress] = useState(0)
    const sendRequest = (request) => {
        setReturnData({})
        setRequestData({
            method: 'POST',
            body: JSON.stringify(request)
        })
        setInProgress(1)
        
    }
    useEffect(() => {
        if (requestData == {}) {return;} 
        else if (inProgress == 0) {return;}
        fetch('http://localhost:42069/api', requestData)
            .then((ret) => {return ret.json();})
            .then((data) => {
                setReturnData(data);
                setInProgress(0)
                setRequestData({})
            });
    }, [requestData, inProgress])
    // useEffect(() => {
    //     setInProgress(1)
    //     const request = {
    //         method: 'POST',
    //         body: JSON.stringify(requestData)
    //     }
    //     console.log(request)
    //     async function reqFetch() {
    //         await fetch('http://localhost:42069/api', request)
    //             .then((res) => {return res.json();})
    //             .then((data) => {
    //                 setData(data);
    //             });
    //     }
    //     reqFetch()
    // },[requestData]);
    // useEffect(() => {setInProgress(0)}, [returnData])
    return {sendRequest, returnData, inProgress}
}

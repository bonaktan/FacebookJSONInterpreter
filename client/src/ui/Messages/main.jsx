import React, {useContext, useEffect, useState} from "react";
import GlobalVariables from "../../globals/globalVariables";
export default function Messages() {
    const Globals = useContext(GlobalVariables)
    const [data, setData] = useState({'Metadata': {'path': ''}, 'Messages': {'inbox': {}}})
    const [inProgress, setInProgress] = useState(true)
    const api = Globals.API
    useEffect(() => {
        api.post('', {'requestType': 'getStructure'}).then((respo) => {
            setData(respo.data['data'])
        })
        setInProgress(false)
    }, [api, setData])

    return (
        <>{inProgress ? 
            <p>Loading, Please Wait.</p> : 
            <>
                <div className="metadata">
                    <p>Name: TBD</p>
                    <p>Location: {data['Metadata']['path']}</p>
                </div>
                <hr />
                <div className='messages'>
                    <p>Messages</p>
                    {Object.entries(data['Messages']['inbox']).map(([convoId, convoData]) => {
                        return <p key={convoId}><a href={'/messages/' + convoId}>{convoData['name']}</a></p>
                    })}
                </div>
            </>
        }</>
    )
}
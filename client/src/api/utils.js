/* eslint-disable react-hooks/exhaustive-deps */
import { useEffect, useRef } from 'react';

export function useUpdateEffect(effect, dependencyArray=[]) {
    const isInitialMount = useRef(true);
    useEffect(() => {
        if (isInitialMount.current) {
            isInitialMount.current = false;
        } else {
            return effect();
        }
    }, dependencyArray);
}

const sleep = ms => new Promise(r => setTimeout(r, ms));
export {sleep};
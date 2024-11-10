export const options = $state({
    query: '',
    useStem: true,
    startDate: '',
    endDate: '',
    operator: 'or'
})

export const modalState = $state({
    isOpen: false
})

export const zipfData:{data:any} = $state({
    data: null
})

export const searchData:{data:any} = $state({
    data: null
})

export interface SearchRecord {
    query: string;
    response_data: any;
}


export const history:SearchRecord[] = $state([])
interface IResponse {
    data?: any;
    message?: string;
    success: boolean;
}
interface ICommunication {
    sendMsg: (action: string, data: any, timeout?: number) => Promise<IResponse>;
    registerEndpoint: (action: string, callback: (data: any) => any) => void;
    sendMsgAsync: (action: string, data: any, rid: string | null) => void;
}
declare const initCommunication: (gid: string) => {
    sendMsg: (action: string, data: any, timeout?: number) => Promise<any>;
    registerEndpoint: (action: string, callback: (data: any) => any) => void;
    sendMsgAsync: (action: string, data: any, rid: string | null) => void;
};
export type { ICommunication };
export default initCommunication;

import React from "react";
interface ModalProps {
    onClose?: () => void;
    hideClose?: boolean;
    show?: boolean;
    title?: string;
}
declare const Modal: React.FC<ModalProps>;
export default Modal;

import React from "react";
import type { IVisSpec } from '@kanaries/graphic-walker/dist/interfaces';
interface IDsaveConfigButtonProps {
    sourceCode: string;
    configJson: IVisSpec[];
    setPygCode: (code: string) => void;
    setTips: (tips: string) => void;
}
declare const saveConfigButton: React.FC<IDsaveConfigButtonProps>;
export default saveConfigButton;

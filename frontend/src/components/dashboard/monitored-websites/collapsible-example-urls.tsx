import { CheckCircle, ChevronDown, ChevronRight, ExternalLink, XCircle } from "lucide-react";
import React from "react";
import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
} from "@/components/ui/collapsible";
import { Button } from "@/components/ui/button";

interface UrlExample {
  url: string;
  displayText: string;
}

interface CollapsibleExampleUrlsProps {
  websiteName: string;
  validUrlExamples: Array<UrlExample>;
  invalidUrlExamples: Array<UrlExample>;
}

export function CollapsibleExampleUrls({
  websiteName,
  validUrlExamples,
  invalidUrlExamples,
}: CollapsibleExampleUrlsProps) {
  const [isOpen, setIsOpen] = React.useState(false);

  return (
    <Collapsible open={isOpen} onOpenChange={setIsOpen} className="w-full">
      <CollapsibleTrigger asChild>
        <Button variant="ghost" className="w-full flex justify-between p-4">
          <span>Show URL examples for {websiteName}</span>
          {isOpen ? (
            <ChevronDown className="h-4 w-4" />
          ) : (
            <ChevronRight className="h-4 w-4" />
          )}
        </Button>
      </CollapsibleTrigger>
      <CollapsibleContent className="space-y-2 p-4 pt-0">
        <div className="space-y-3">
          <div>
            <ul className="space-y-2">
              {validUrlExamples.map((example, index) => (
                <li key={index} className="flex items-start">
                  <CheckCircle className="h-4 w-4 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                  <span className="text-sm break-all flex-1 overflow-hidden">{example.displayText}</span>
                  <a
                    href={example.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="ml-2 text-green-500 hover:text-green-700 flex-shrink-0"
                  >
                    <ExternalLink className="h-4 w-4" />
                  </a>
                </li>
              ))}
            </ul>
          </div>
          <div>
            <ul className="space-y-2">
              {invalidUrlExamples.map((example, index) => (
                <li key={index} className="flex items-start">
                  <XCircle className="h-4 w-4 text-red-500 mr-2 mt-0.5 flex-shrink-0" />
                  <span className="text-sm break-all flex-1 overflow-hidden">{example.displayText}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </CollapsibleContent>
    </Collapsible>
  );
}

import { ExternalLink } from "lucide-react";
import { useTranslation } from "react-i18next";
import { CollapsibleExampleUrls } from "./collapsible-example-urls";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";

interface SupportedWebsitesModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function SupportedWebsitesModal({ isOpen, onClose }: SupportedWebsitesModalProps) {
  const { t } = useTranslation();

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>{t('dashboard.monitoredWebsites.supportedWebsites.title')}</DialogTitle>
          <DialogDescription>
            {t('dashboard.monitoredWebsites.supportedWebsites.description')}
          </DialogDescription>
        </DialogHeader>
        <div className="p-4 bg-warning/10 border border-warning/30 rounded-lg">
          <h3 className="font-medium text-lg text-warning flex items-center">
            <span className="inline-flex items-center justify-center w-6 h-6 rounded-full bg-warning text-warning-foreground mr-2" aria-hidden="true">!</span>
            {t('dashboard.monitoredWebsites.supportedWebsites.howToGetUrl')}
          </h3>
          <ol className="list-decimal list-inside space-y-2 text-sm text-muted-foreground mt-2">
            <li>{t('dashboard.monitoredWebsites.supportedWebsites.step1')}</li>
            <li>{t('dashboard.monitoredWebsites.supportedWebsites.step2')}</li>
            <li className="font-medium text-warning">{t('dashboard.monitoredWebsites.supportedWebsites.step3')}</li>
            <li>{t('dashboard.monitoredWebsites.supportedWebsites.step4')}</li>
          </ol>
        </div>
        <div className="space-y-6 py-4">
          <div className="space-y-4">
            <h3 className="font-medium text-lg">{t('dashboard.monitoredWebsites.supportedWebsites.currentlySupported')}</h3>

            <div className="space-y-3">
              <div className="p-4 bg-card rounded-lg border border-border">
                <div className="flex items-center justify-between">
                  <h4 className="font-medium">OLX</h4>
                  <a
                    href="https://www.olx.pl/"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-primary hover:text-primary/80 flex items-center text-sm focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 rounded"
                    aria-label={`${t('dashboard.monitoredWebsites.supportedWebsites.visitWebsite')} (opens in new tab)`}
                  >
                    {t('dashboard.monitoredWebsites.supportedWebsites.visitWebsite')}
                    <ExternalLink className="w-4 h-4 ml-1" aria-hidden="true" />
                  </a>
                </div>
                <p className="text-sm text-muted-foreground mt-2">
                  {t('dashboard.monitoredWebsites.supportedWebsites.olxInstructions')}
                </p>
                <CollapsibleExampleUrls
                  websiteName="OLX"
                  validUrlExamples={[
                    {
                      url: "https://www.olx.pl/nieruchomosci/mieszkania/?search%5Bfilter_float_price:to%5D=700",
                      displayText: "https://www.olx.pl/nieruchomosci/mieszkania/"
                    },
                    {
                      url: "https://www.olx.pl/motoryzacja/samochody/?search%5Bfilter_float_price%3Afrom%5D=31000&search%5Bfilter_float_price%3Ato%5D=31100",
                      displayText: "https://www.olx.pl/motoryzacja/samochody/"
                    }
                  ]}
                  invalidUrlExamples={[
                    {
                      url: "https://www.olx.pl/d/oferta/citroen-berlingo-xl-CID5-ID17exAm.html",
                      displayText: "https://www.olx.pl/d/oferta/citroen-berlingo-xl-CID5-ID17exAm.html"
                    }
                  ]}
                />
              </div>
            </div>
          </div>


        </div>

        <DialogFooter>
          <Button onClick={onClose}>
            {t('dashboard.monitoredWebsites.supportedWebsites.closeButton')}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}

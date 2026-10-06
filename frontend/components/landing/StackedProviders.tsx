import React from "react";
import { cn } from "@/lib/utils";
import { motion, LayoutGroup } from "framer-motion";

export function StackedProviders() {
  const stack: string[] = ["Google Drive", "OneDrive", "Dropbox"];

  return (
    <div className="mt-4 flex-wrap w-full gap-1 flex items-center justify-start">
      <LayoutGroup>
        {stack.map((item, idx) => (
          <StackItem
            key={item + idx}
            technology={item}
            className="-mr-3 hover:z-10 bg-white/70 backdrop-blur-md border border-orange-200 shadow-sm"
          />
        ))}
      </LayoutGroup>
    </div>
  );
}

const StackItem = ({
  technology,
  className,
}: {
  technology: string;
  className?: string;
}) => {
  const getLogoForTechnology = (technology: string) => {
    const logoMap: Record<string, React.ReactNode> = {
      "Google Drive": <GoogleDriveLogo className="size-5 shrink-0" />,
      "OneDrive": <OneDriveLogo className="size-5 shrink-0" />,
      "Dropbox": <DropboxLogo className="size-5 shrink-0" />,
    };

    return logoMap[technology];
  };

  return (
    <motion.div
      layout
      whileHover="animate"
      whileTap="animate"
      initial="initial"
      className={cn(
        "flex items-center justify-start rounded-full p-1 text-sm text-gray-700 cursor-pointer overflow-hidden",
        "h-[36px] min-w-[36px]",
        className,
      )}
    >
      <motion.div
        variants={{
          initial: { paddingRight: 0 },
          animate: { paddingRight: 8 },
        }}
        transition={{ type: "spring" }}
        className="flex items-center justify-center shrink-0 w-7 h-7"
      >
        {getLogoForTechnology(technology)}
      </motion.div>
      <motion.div
        variants={{
          initial: { width: 0, opacity: 0 },
          animate: { width: "auto", opacity: 1 },
          exit: { width: 0, opacity: 0 },
        }}
        transition={{
          type: "spring",
          stiffness: 200,
          damping: 25,
          mass: 0.5,
        }}
        className="overflow-hidden whitespace-nowrap"
      >
        <span className="text-gray-800 font-semibold pr-2">
          {technology}
        </span>
      </motion.div>
    </motion.div>
  );
};

export const GoogleDriveLogo = (props: React.SVGProps<SVGSVGElement>) => (
  <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" {...props}>
    <path d="M12 10l-6 10l-3 -5l6 -10l3 5" fill="#4285F4" />
    <path d="M9 15h12l-3 5h-12" fill="#34A853" />
    <path d="M15 15l-6 -10h6l6 10l-6 0" fill="#FBBC05" />
  </svg>
);

export const OneDriveLogo = (props: React.SVGProps<SVGSVGElement>) => (
  <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" {...props}>
    <path fill="#0078D4" d="M18.456 10.45a6.45 6.45 0 0 0 -12 -2.151a4.857 4.857 0 0 0 -4.44 5.241a4.856 4.856 0 0 0 5.236 4.444h10.751a3.771 3.771 0 0 0 3.99 -3.54a3.772 3.772 0 0 0 -3.538 -3.992l.001 -.002" />
  </svg>
);

export const DropboxLogo = (props: React.SVGProps<SVGSVGElement>) => (
  <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" {...props} className={cn("translate-y-[1.5px]", props.className)}>
    <path fill="#0061FE" d="M6 1.807L0 5.629l6 3.822 6.001-3.822L6 1.807zM18 1.807l-6 3.822 6 3.822 6-3.822-6-3.822zM0 13.274l6 3.822 6.001-3.822L6 9.452l-6 3.822zM18 9.452l-6 3.822 6 3.822 6-3.822-6-3.822zM6 18.371l6.001 3.822 6-3.822-6-3.822L6 18.371z"/>
  </svg>
);

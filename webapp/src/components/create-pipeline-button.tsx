import { Button, Modal } from "flowbite-react";
import { useState } from "react";
import { CreatePipelineForm } from "./create-pipeline-form";

export default function CreatePipelineButton() {
  const [openModal, setOpenModal] = useState<string | undefined>();

  return (
    <>
      <Button color="blue" onClick={() => setOpenModal("create-pipeline-form")}>
        Create Pipeline
      </Button>
      <Modal
        show={openModal === "create-pipeline-form"}
        popup
        onClose={() => setOpenModal(undefined)}
      >
        <Modal.Header />
        <Modal.Body>
          <div className="mt-4">
            <CreatePipelineForm />
          </div>
        </Modal.Body>
      </Modal>
    </>
  );
}

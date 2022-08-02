#! Python 3
from botbuilder.dialogs import ComponentDialog, WaterfallDialog, WaterfallStepContext, DialogTurnResult  # all these are the Dialog libraries. remember bot sdk provides message/activity handler, dialog libraries and custom bot class and custom logic
from botbuilder.dialogs.prompts import (
    TextPrompt,
    NumberPrompt,
    ChoicePrompt,
    ConfirmPrompt,
    AttachmentPrompt,
    PromptOptions,
    PromptValidatorContext
)
from botbuilder.dialogs.choices import Choice
from botbuilder.core import MessageFactory, UserState

from data_models import UserProfile


class UserProfileDialog(
    ComponentDialog):  # this is where the steps for the dialog is defined, i.e the prompts and the waterfall steps
    def __init__(self, user_state: UserState):
        super(UserProfileDialog, self).__init__(UserProfileDialog.__name__)

        """here we are trying to define all the prompts for the user and followed by adding it to a dialog set"""

        self.user_profile_accessor = user_state.create_property(
            "UserProfile")  # creates an entry(more like a database) for this dialog in the memory

        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    self.name_step,
                    self.purpose_of_negotiation_step,
                    self.negotiation_confirm_step,
                    self.product_type_step,
                    self.price_to_negotiate_step,
                    self.picture_of_item_step,
                    self.confirm_step,
                    self.summary_step,
                ],
            )
        )
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(NumberPrompt(NumberPrompt.__name__, UserProfileDialog.price_to_negotiate_prompt_validator))
        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))
        self.add_dialog(
            AttachmentPrompt(
                AttachmentPrompt.__name__, UserProfileDialog.picture_of_item_prompt_validator
            )
        )
        """these are the different prompts that would be needed"""

        self.initial_dialog_id = WaterfallDialog.__name__

    async def name_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(prompt=MessageFactory.text("Hi, Welcome!\n Can I Have your Name?")),
        )

    async def purpose_of_negotiation_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        step_context.values["name"] = step_context.result

        await step_context.context.send_activity(
            MessageFactory.text(f"Thanks {step_context.result}")
        )

        return await step_context.prompt(
            ChoicePrompt.__name__,
            PromptOptions(
                prompt=MessageFactory.text(f"Ok! {step_context.result}\n Can you select the purpose of this price negotiation?"),
                choices=[Choice("Too high"), Choice("too low"), Choice("no price")],
            ),
        )

    async def negotiation_confirm_step(
            self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        step_context.values["purpose_of_negotiation"] = step_context.result.value

        return await step_context.prompt(
            ConfirmPrompt.__name__,
            PromptOptions(
                prompt=MessageFactory.text("Would you like to begin negotiation Process?")
            ),
        )


    async def product_type_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        if step_context.result:
            return await step_context.prompt(
                ChoicePrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("what Category or sub-category does the product fall under?."),
                    choices=[Choice("Fashion"), Choice("Phones and Tablets"), Choice("electronics"), Choice("Others")]  # take note of the caps
                ),
            )

        await step_context.context.send_activity(MessageFactory.text("thank you for your feedback"))
        return await step_context.end_dialog()

    async def price_to_negotiate_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
        step_context.values["product_type"] = step_context.result
        if not step_context.result:
            await step_context.context.send_activity(MessageFactory.text("so Proceed to payment at www.e-commerce.com"))
            return await step_context.next(0)
        return await step_context.prompt(NumberPrompt.__name__,
                                         PromptOptions(
                                             prompt=MessageFactory.text("please Enter your negotiation price"),
                                             retry_prompt=MessageFactory.text("negotiation price cannot be blank or negative")
                                         ),
                                         )


    async def picture_of_item_step(
            self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        step_context.values["price_to_negotiate"] = step_context.result

        if step_context.values["price_to_negotiate"] != 0:
            await step_context.context.send_activity(MessageFactory.text(f"i have your bid at {step_context.result}"))
            if step_context.context.activity.channel_id == "msteams":
                await step_context.context.send_activity(
                    "Skipping attachment prompt in Teams channel..."
                )
                return await step_context.next(None)

            prompt_options = PromptOptions(
                prompt=MessageFactory.text(
                    "Please attach a picture of the item you're negotiating."
                ),
                retry_prompt=MessageFactory.text(
                    "The attachment must be a jpeg/png image file."
                ),
            )
            return await step_context.prompt(AttachmentPrompt.__name__, prompt_options)
        return await step_context.next(None)

    async def confirm_step(
            self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        step_context.values["picture_of_item"] = (
            None if not step_context.result else step_context.result[0]
        )

        return await step_context.prompt(
            ConfirmPrompt.__name__,
            PromptOptions(prompt=MessageFactory.text("verify all is set!")),
        )

    async def summary_step(
            self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        if step_context.result:
            user_profile = await self.user_profile_accessor.get(
                step_context.context, UserProfile
            )

            user_profile.name = step_context.values["name"]
            user_profile.product_type = step_context.values["product_type"]
            user_profile.purpose_of_negotiation = step_context.values["purpose_of_negotiation"]
            user_profile.price_of_negotiation = step_context.values["price_to_negotiate"]
            user_profile.picture_of_item = step_context.values["picture_of_item"]

            msg = f"I have your purpose of negotiation as {user_profile.purpose_of_negotiation} and your name as {user_profile.name}."
            if not user_profile.product_type:
                msg += f" And product type as {user_profile.product_type}."

            await step_context.context.send_activity(MessageFactory.text(msg))

            if user_profile.picture_of_item:
                await step_context.context.send_activity(
                    MessageFactory.attachment(
                        user_profile.picture_of_item, "This is the item you want to negotiate price on."
                    )
                )
            else:
                await step_context.context.send_activity(
                    "No picture was provided for the item you want to negotiate on."
                )
        await step_context.context.send_activity(
                MessageFactory.text("Thanks. Your Negotiation Request is being reviewed.")
            )

        return await step_context.end_dialog()

    @staticmethod
    async def price_to_negotiate_prompt_validator(
            prompt_context: PromptValidatorContext) -> bool:  # note the prompt validator context name.... returns a boolean
        return (
                prompt_context.recognized.succeeded
                and 0 < prompt_context.recognized.value < 999999
        )

    @staticmethod
    async def picture_of_item_prompt_validator(
            prompt_context: PromptValidatorContext) -> bool:  # note the prompt validator context name.... returns a a boolean
        if not prompt_context.recognized.succeeded:  # recognized is part of the validator context property, alongside context and options(these weren't used here).
            await prompt_context.context.send_activity(
                "No attachments received. Proceeding without a profile picture..."
            )

            # We can return true from a validator function even if recognized.succeeded is false.
            return True

        attachments = prompt_context.recognized.value

        valid_images = [
            attachment
            for attachment in attachments
            if attachment.content_type in ["image/jpeg", "image/png"]
        ]

        prompt_context.recognized.value = valid_images

        return len(valid_images) > 0

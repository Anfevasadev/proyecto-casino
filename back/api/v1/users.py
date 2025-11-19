from datetime import datetime

from fastapi import APIRouter, HTTPException, Path, status

from back.domain.users.update import NotFoundError, update_user
from back.models.users import UserOut, UserUpdate
from back.storage import users_repo as repo


router = APIRouter()


def _clock_local() -> str:
	# Formato local sencillo; README menciona YYYY-MM-DD HH:MM:SS
	return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@router.put("/{user_id}", response_model=UserOut, status_code=status.HTTP_200_OK)
def put_user(
	user_id: int = Path(..., ge=1),
	body: UserUpdate | None = None,
):
	if body is None:
		body = UserUpdate()

	try:
		updated = update_user(
			user_id=user_id,
			cambios=body.model_dump(exclude_unset=True),
			clock=_clock_local,
			repo=repo,
			actor="api",
		)
		return UserOut(**updated)
	except NotFoundError as e:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
	except ValueError as e:
		raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
